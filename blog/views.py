from django.shortcuts import render, redirect
from .models import Post, Category, Tag, Comment                             # 카테고리부분
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from .forms import CommentForm
from django.shortcuts import get_object_or_404

# Create your views here.
class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']  # , 'tags'
    # 템플릿 post_form

    template_name = 'blog/post_update_form.html' # 클래스에서도 직접적으로 템플릿을 부를 수 있다.

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def form_valid(self, form):
        response = super(PostUpdate, self).form_valid(form)
        self.object.tags.clear()
        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')
            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)  # 태그 기존에 있는 거 가져오든지 아님 새로 만드는 행동함.
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)  # 슬러그까지 추가해서 저장.
                    tag.save()
                self.object.tags.add(tag)
        return response

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()                # string 배열들로 만들고 하나의 string으로 만듦.
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = ';'.join(tags_str_list)      # 다 합쳐서 각각을 ;으로 구분하게 만듦.
        context['categories'] = Category.objects.all()                                   # 카테고리부분 사이드바 내용 위해 추가해줌.
        context['no_category_post_count'] = Post.objects.filter(category=None).count
        return context

class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title','hook_text', 'content', 'head_image', 'file_upload','category'] # , 'tags' 태그 구분 딜리미터 , ; 만 씀.
    # 템플릿 post_form
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_superuser or current_user.is_staff):
            form.instance.author = current_user
            response = super(PostCreate, self).form_valid(form)
            tags_str = self.request.POST.get('tags_str') # POST 우리가 쓰고 있는 모델명이 아니라 사용자가 request할 떄 URL없이 비교적 긴 데이터 전달할 때 쓰는 전달 방식
            if tags_str :
                tags_str = tags_str.strip()
                tags_str = tags_str.replace(',',';')
                tags_list = tags_str.split(';')
                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)       # 태그 기존에 있는 거 가져오든지 아님 새로 만드는 행동함.
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode = True)               # 슬러그까지 추가해서 저장.
                        tag.save()
                    self.object.tags.add(tag)
            return response
        else:
            return redirect('/blog/')

    # 템플릿 : 모델명_form.html
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostCreate, self).get_context_data()
        context['categories'] = Category.objects.all()                                   # 카테고리부분 사이드바 내용 위해 추가해줌.
        context['no_category_post_count'] = Post.objects.filter(category=None).count
        return context

class PostList(ListView):
    model = Post
    ordering = '-pk' # 모델 이름만 설정하면 자동 호출 pk값이 작은 순서대로 보여달란 뜻임.
    paginate_by = 5 # 페이지네이션, 내용 나눠서 보여주는 것

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()                                   # 카테고리부분
        context['no_category_post_count'] = Post.objects.filter(category=None).count
        return context

    # 템플릿 모델명_list.html : post_list.html
    # 파라미터 모델명_list : post_list

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):     # 카테고리부분
        context = super(PostDetail, self).get_context_data()    # 슈퍼 해당되는 내용 PostDetail임을 명심하자
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count
        context['comment_form'] = CommentForm
        return context

def category_page(request, slug):
    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)                     # 카테고리부분
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)
    return render(request, 'blog/post_list.html', {
        'category' : category,                                        # 템플릿이 사용하는 변수는 따옴표 안에 있음 :은 =과 같은 역할
        'post_list' : post_list,
        'categories' : Category.objects.all(),
        'no_category_post_count' : Post.objects.filter(category=None).count
    })

def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()
    return render(request, 'blog/post_list.html', {
        'tag' : tag,
        'post_list': post_list,
        'categories': Category.objects.all(),
        'no_category_post_count': Post.objects.filter(category=None).count
    })

    # 템플릿 모델명_detail.html : post_detail.html
    # 파라미터 모델명 : post

def new_comment(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)
        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url())
        else: # GET
            return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied

class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    # CreateView, UpdateView, form을 사용하면
    # 템플릿 모델명_form : comment_form

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


# CBV방식에는 이게 필요함. 글 여러개 나타낼 때 필요 for문에서 post
#def index(request):
#    posts1 =Post.objects.all().order_by('-pk')    최신 포스트 부터 보여주기
#    return render(request, 'blog/index.html', {'posts': posts1})

#def single_post_page(request,pk):
#    post2 = Post.objects.get(pk=pk)
#    return render(request,'blog/single_post_page.html', {'post':post2})