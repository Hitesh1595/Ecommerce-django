from django.db import models

from category.models import Category
from accounts.models import Account

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
    
    # calculate the avg rating 
    # average can be any name as you wish
    def averageReview(self):

        from django.db.models import Avg

        reviews = ReviewRating.objects.filter(product = self,status = True).aggregate(average = Avg('rating'))
        avg = 0
        if reviews['average']:
            avg = float(reviews['average'])
        
        return avg
    
    def countReview(self):
        from django.db.models import Count
        reviews = ReviewRating.objects.filter(product = self,status = True).aggregate(count = Count('id'))
        count = 0
        if reviews['count']:
            count = int(reviews['count'])
        
        return count



# is used to categoried or diffrenciate on the basis of ''variation_category'' as we passes
# instead of pass all we have to pass colors or sizes so it will pass only those category value 
class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(variation_category = 'color',is_active = True)

    def sizes(self):
        return super(VariationManager,self).filter(variation_category = 'size',is_active = True)

variation_category_choice = (
    ('color','color'),
    ('size' , 'size')
)


class Variation(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100,choices=variation_category_choice) 
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()


    # make object like record
    def __str__(self):
        return self.variation_value



class ReviewRating(models.Model):
    product = models.ForeignKey(Product,on_delete = models.CASCADE)
    user =  models.ForeignKey(Account,on_delete=models.CASCADE)
    subject = models.CharField(max_length=100,blank = True)
    review = models.CharField(max_length=500,blank = True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20,blank = True)
    status = models.BooleanField(default = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.subject


class ProductGallery(models.Model):
    product = models.ForeignKey(Product,default = None,on_delete=models.CASCADE)
    image = models.ImageField(upload_to = "store/products",max_length=255)

    def __str__(self):
        return self.product.product_name
    
    class Meta:
        verbose_name = "productgallery"
        verbose_name_plural = "product gallery"