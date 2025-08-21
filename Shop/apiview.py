from .serializers import UserSerializer,ShopMasterSerializer,ItemMasterSerializer,AccessRequestSerializer,AccessRequestAdminSerializer,RegisterSerializer
from rest_framework import viewsets,permissions,generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models  import  User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from django.db.models import Sum,DecimalField,ExpressionWrapper,F
import pandas as pd
from .models import ShopMaster,ItemMaster,InventorySummary,SalesSummary,ReceiveLog,AccessRequest
from datetime import timedelta,date
from django.shortcuts import get_object_or_404
from rest_framework import status






class AccessRequestApi(APIView):

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AccessRequestSerializer
        return AccessRequestAdminSerializer

    
    def post(self, request):
        serializer = AccessRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    
    def get(self, request,pk = None):
        queryset = AccessRequest.objects.all()
        if pk:
            queryset = AccessRequest.objects.filter(pk=pk)
        serializer = AccessRequestAdminSerializer(queryset, many=True)
        return Response(serializer.data)

    def patch(self, request, pk=None):
        access_request = get_object_or_404(AccessRequest, pk=pk)
        serializer = AccessRequestAdminSerializer(
            access_request, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk=None):
        access_request = get_object_or_404(AccessRequest, pk=pk)
        access_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CurrentUserDetails(generics.RetrieveUpdateAPIView):
        queryset = User.objects.all()
        serializer_class = UserSerializer
        permission_classes = [permissions.IsAuthenticated]

        def get_object(self):
                 return self.request.user
        

class Shop(generics.ModelViewSet):
    serializer_class = ShopMasterSerializer

    def get_queryset(self):
        user = self.request.user
        return ShopMaster.objects.filter(profile_company_id=user.companyprofile)



class Item(viewsets.ModelViewSet):
    serializer_class = ItemMasterSerializer

    def get_queryset(self):
        user = self.request.user
        return ItemMaster.objects.filter(profile_company_id=user.companyprofile)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Inventroy(request):
    user = request.user
    company = user.companyprofile

    
    # Filters 
    shop_filter = request.GET.get('shop')
    item_filter = request.GET.get('item')

    # Base Query
    summaries = InventorySummary.objects.filter(
        shop__profile_company_id=company).select_related('shop', 'item')
    
    # Filter Conditions
    if shop_filter:
        summaries = summaries.filter(shop_id=shop_filter)
    if item_filter:
        summaries = summaries.filter(item_id=item_filter)


    # Shop-wise Inventory  Summary and Column Total
    shop_wise = summaries.values('shop__name').annotate(
        total_stock_value=Sum('stock_value'),
        total_available_qty=Sum('available_qty'),
    )

    total_summary = shop_wise.aggregate(total_qty=Sum('available_qty'), total_cost=Sum('stock_value'))
    shop_summary = list(shop_wise) + [{'shop__name': 'Total', **total_summary}]


    # Low Stock Items
    low_stock = list(summaries.filter(available_qty__lt=10).values(
        'item__name', 'shop__name', 'available_qty'
    ))    

    # Item-wise Report (Shop-wise Qty) :- Pivot Data
    pivot_data = summaries.values('item__name', 'shop__name', 'available_qty')
    df = pd.DataFrame(pivot_data)

    if df.empty:
        item_data = [["No data"]]
    else:
        pivot_df = pd.pivot_table(
            df,
            index='item__name',
            columns='shop__name',
            values='available_qty',
            aggfunc='sum',
            fill_value=0
        )

       
        if not shop_filter:
            pivot_df['Total'] = pivot_df.sum(axis=1)
        pivot_df.loc['Total'] = pivot_df.sum()

       
        item_data = [pivot_df.columns.insert(0, 'Item Name').tolist()]
        for index, row in pivot_df.iterrows():
            item_data.append([index] + row.tolist())



    return Response({
        'selected_shop': shop_filter,
        'selected_item': item_filter,
        'shop_summary': shop_summary,
        'item_data':item_data,
        'low_stock': low_stock
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Receive(request):
    user = request.user
    company = user.companyprofile

    # Filters 
    from_date = request.GET.get('from_date') or str(date.today() - timedelta(days=30))
    to_date = request.GET.get('to_date') or str(date.today())
    shop_filter = request.GET.get('shop')
    item_filter = request.GET.get('item')

    # Base Query  and Receive Transaction
    receives_qs = ReceiveLog.objects.filter(
        shop__profile_company_id=company,
        date__range=[from_date, to_date]
    )
    # Filter Conditions
    if shop_filter:
        receives_qs = receives_qs.filter(shop_id=shop_filter)
    if item_filter:
        receives_qs = receives_qs.filter(item_id=item_filter)
    # Shop-wise Receive Summary and Column Total
    shop_summary_data = receives_qs.values('shop__name').annotate(
        total_qty=Sum('qty'),
        total_cost=Sum('rate')
    )
    total_summary = receives_qs.aggregate(total_qty=Sum('qty'), total_cost=Sum('rate'))
    shop_summary = list(shop_summary_data) + [{'shop__name': 'Total', **total_summary}]

    # Item-wise Receive Report :- Pivot Data
    pivot_data = receives_qs.values('item__name', 'shop__name', 'qty', 'rate')
    df = pd.DataFrame(pivot_data)

    if df.empty:
        item_data = [["No data"]]
    else:
        pivot_df = pd.pivot_table(
            df,
            index='item__name',
            columns='shop__name',
            values='qty',
            aggfunc='sum',
            fill_value=0
        )

       
        if not shop_filter:
            pivot_df['Total'] = pivot_df.sum(axis=1)
        pivot_df.loc['Total'] = pivot_df.sum()

       
        item_data = [pivot_df.columns.insert(0, 'Item Name').tolist()]
        for index, row in pivot_df.iterrows():
            item_data.append([index] + row.tolist())
    print("shop_summary = ",shop_summary)
    print("receives_qs = ",receives_qs)    

    return Response({
        
        'selected_shop': shop_filter,
        'selected_item': item_filter,
        'from_date': from_date,
        'to_date': to_date,

        'shop_summary': shop_summary,
        'item_data': item_data,
        'receives':receives_qs.order_by('-date').values_list()


    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Sales(request):
    user = request.user
    company = user.companyprofile
    
  
    # Filters 
    from_date = request.GET.get('from_date') or str(date.today() - timedelta(days=30))
    to_date = request.GET.get('to_date') or str(date.today())
    shop_filter = request.GET.get('shop')
    item_filter = request.GET.get('item')
    payment_type_filter = request.GET.get('payment_type')

   
    # Base Query and Sales transaction
    sales_qs = SalesSummary.objects.filter(
        shop__profile_company_id=company,
        sale_date__range=(from_date, to_date)
    )

    # Filter Condtions
    if shop_filter:
        sales_qs = sales_qs.filter(shop_id=shop_filter)
    if item_filter:
        sales_qs = sales_qs.filter(item_id=item_filter)
    if payment_type_filter:
        sales_qs = sales_qs.filter(payment_type=payment_type_filter)
    
    # Top Selling Items
    top_items = sales_qs.values('item__name').annotate(
        total_qty=Sum('qty_sold')
    ).order_by('-total_qty')[:5].values_list()


    # Pivot Data Frame
    pivot_data = sales_qs.values('item__name', 'shop__name', 'total_amt', 'sale_date','payment_type')
    df = pd.DataFrame(pivot_data)

    # Revenue by Payment Method :- Pivot Data
    if df.empty:
        payment_data = [["No data"]]
    else:
        payment_pivot = pd.pivot_table(
            df,
            index='payment_type',
            columns='shop__name',
            values='total_amt',
            aggfunc='sum',
            fill_value=0
        )
        if not shop_filter:
            payment_pivot['Total'] = payment_pivot.sum(axis=1)

        payment_pivot.loc['Total'] = payment_pivot.sum()
        payment_data = [payment_pivot.columns.insert(0, 'Payment Type').tolist()]
        for index, row in payment_pivot.iterrows():
            payment_data.append([index] + row.tolist())


    # Shop Wise Revenue :- Pivot Data
    if df.empty:
        revenue_data = [["No data"]]
    else:
        revenue_pivot = pd.pivot_table(
            df,
            index='item__name',
            columns='shop__name',
            values='total_amt',
            aggfunc='sum',
            fill_value=0
        )

        if not shop_filter:
            revenue_pivot['Total'] = revenue_pivot.sum(axis=1)

        revenue_pivot.loc['Total'] = revenue_pivot.sum()
        revenue_data = [revenue_pivot.columns.insert(0, 'Item Name').tolist()]
        for index, row in revenue_pivot.iterrows():
            revenue_data.append([index] + row.tolist())
    
    # Date Wise Sales :- Pivot Data
    if df.empty:
        date_data = [["No data"]]
    else:
        date_pivot = pd.pivot_table(
            df,
            index='shop__name',
            columns='sale_date',
            values='total_amt',
            aggfunc='sum',
            fill_value=0,
            margins=True,
            margins_name='Total' 

        )
        date_data = [date_pivot.columns.insert(0, 'Date').tolist()]
        for index, row in date_pivot.iterrows():
            date_data.append([index] + row.tolist())
   
    return Response({
        
        'selected_shop': shop_filter,
        'selected_item': item_filter,
        'selected_payment':payment_type_filter,
        'from_date': from_date,
        'to_date': to_date,
        
        'date_data': date_data,
        'revenue_data': revenue_data,
        'payment_data':payment_data,
        'top_items': top_items,
        'sales':sales_qs.order_by('-sale_date').values_list()
       
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Profitability(request):
    user = request.user
    company = user.companyprofile

    # Filters
    from_date = request.GET.get('from_date') or str(date.today() - timedelta(days=30))
    to_date = request.GET.get('to_date') or str(date.today())
    shop_filter = request.GET.get('shop')
    item_filter = request.GET.get('item')
    payment_type_filter = request.GET.get('payment_type')

    
    # Base Query
    sales_qs = SalesSummary.objects.filter(
        shop__profile_company_id=company,
        sale_date__range=(from_date, to_date)
    )
    # Filter Conditions 
    if shop_filter:
        sales_qs = sales_qs.filter(shop_id=shop_filter)
    if item_filter:
        sales_qs = sales_qs.filter(item_id=item_filter)
    if payment_type_filter:
        sales_qs = sales_qs.filter(payment_type=payment_type_filter)

    
    sales_qs = sales_qs.annotate(
        cost_total=F('cost_rate') * F('qty_sold'),
        profit_margin=ExpressionWrapper(
            (F('profit') / (F('cost_rate') * F('qty_sold'))) * 100,
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    )

    
    
    # Shop  Wise Profit
    shop_profit = sales_qs.values('shop__name').annotate(total_profit=Sum('profit')).order_by('-total_profit')
    # Item Wise  Profit
    item_profit = sales_qs.values('item__name').annotate(total_profit=Sum('profit')).order_by('-total_profit')[:10]
    return Response({
      
        'selected_shop': shop_filter,
        'selected_item': item_filter,
        'selected_payment':payment_type_filter,
        'from_date': from_date,
        'to_date': to_date,
        
        'shop_profit': shop_profit,
        'item_profit': item_profit,
      
        
    })


