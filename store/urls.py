from django.urls import path


from .views import CategoryView, CategoryDetailView, ProductView, ProductDetailView, PromotionView, PromotionDetailView, \
    CartHistoryView, CartView

urlpatterns = [
    path('store/categories/', CategoryView.as_view(), name='get_create_category'),
    path('store/categories/<int:category_id>/', CategoryDetailView.as_view(), name='update_delete_category'),
    path('store/products/', ProductView.as_view(), name='get_create_product'),
    path('store/products/<int:product_id>/', ProductDetailView.as_view(), name='update_delete_product'),
    path('store/promotions/', PromotionView.as_view(), name='get_create_promotion'),
    path('store/promotions/<int:promotion_id>/', PromotionDetailView.as_view(), name='update_delete_promotion'),
    path('store/carts/', CartHistoryView.as_view()),
    path('store/carts/current/', CartView.as_view(), name='cart_detail')
]
