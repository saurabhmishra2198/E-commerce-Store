from django.contrib import admin
from SaurabhComputerApp.models import Product,Contact,Orders,OrderUpdate,Blogpost,Services
# Register your models here.

admin.site.register(Product)
admin.site.register(Contact)
admin.site.register(Orders)
admin.site.register(OrderUpdate)
admin.site.register(Blogpost)
admin.site.register(Services)