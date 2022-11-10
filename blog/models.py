from django.db import models
from django.contrib.auth.models import User  # 작성자 할 때 추가
import os

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):  # IP주소/blog/tag/slug
        return f'/blog/tag/{self.slug}/'

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):                             # 카테고리부분
        return f'/blog/category/{self.slug}'

    class Meta:                                               # 카테고리부분
        verbose_name_plural = 'Categories'

class Post(models.Model):
    title = models.CharField(max_length=30)
    hook_text = models.CharField(max_length=100, blank=True)
    content = models.TextField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True)   # blank=True라고 하면 필수항목은 아니라는 뜻
    # %Y 2022, %y 22
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 추후 author 작성
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL) # null은 null이라는 값을 넣을수 있는것..  blank가 있어야 카테고리없는 거 허용
    tags = models.ManyToManyField(Tag, null=True, blank=True) # null = True 포함되어 있어서 적을 필요없음 on_delete도 마찬가지임.

    def __str__(self):
        return f'[{self.pk}]{self.title}:: {self.author} : {self.created_at}'

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):  # 템플릿에서 쓰는 이름과 반드시 같아야 한다.
        return self.get_file_name().split('.')[-1]  # 가장 마지막 배열의 원소. -1
        # a.txt  -> a txt
        # b.docx -> b docx
        # c.xlsx -> c xlsx
        # a.b.c.txt -> a b c txt