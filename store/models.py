from django.db import models

from category.models import Category

from django.urls import reverse

# Create your models here.

class Product(models.Model):
    product_name     = models.CharField(max_length = 200,unique = True)
    slug             = models.SlugField(max_length = 200,unique = True)
    description      = models.TextField(max_length = 250,blank = True)
    price            = models.IntegerField()
    images           = models.ImageField(upload_to = 'photos/products')
    stock            = models.IntegerField()
    is_available     = models.BooleanField(default = True)

    # product category  is connect with predefined link category 
    # if main category delete then all related items are also delete automatically
    category         = models.ForeignKey(Category,on_delete = models.CASCADE)
    # set once when product is created
    created_date     = models.DateTimeField(auto_now_add = True)
    # modified every time when any field value changes
    modified_date    = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.product_name

    # for routing to speecific page 
    def get_url(self):
        return reverse('store:product_detail',args = [self.category.slug, self.slug])