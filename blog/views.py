from django.shortcuts import render, redirect
from .models import Post, Category, Tag                             # 카테고리부분
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

# Create your views here.
class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category', 'tags']

    template_name = 'blog/post_update_form.html' # 클래스에서도 직접적으로 템플릿을 부를 수 있다.

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        context['categories'] = Category.objects.all()                                   # 카테고리부분 사이드바 내용 위해 추가해줌.
        context['no_category_post_count'] = Post.objects.filter(category=None).count
        return context

class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title','hook_text', 'content', 'head_image', 'file_upload','category']

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_superuser or current_user.is_staff):
            form.instance.author = current_user
            return super(PostCreate, self).form_valid(form)
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

# CBV방식에는 이게 필요함. 글 여러개 나타낼 때 필요 for문에서 post
#def index(request):
#    posts1 =Post.objects.all().order_by('-pk')    최신 포스트 부터 보여주기
#    return render(request, 'blog/index.html', {'posts': posts1})

#def single_post_page(request,pk):
#    post2 = Post.objects.get(pk=pk)
#    return render(request,'blog/single_post_page.html', {'post':post2})