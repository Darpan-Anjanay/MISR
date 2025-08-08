from django.contrib.auth.decorators import login_required
from django.db.models import Sum,F, DecimalField, FloatField, Count, ExpressionWrapper
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import ShopMaster, InventorySummary, SalesSummary, ReceiveLog, ItemMaster
from .forms import ItemForm, ShopForm
from datetime import datetime, timedelta,date
from django.views.decorators.http import require_GET
import pandas as pd
from dateutil.relativedelta import relativedelta
from django.contrib import messages

# Profile
@login_required(login_url='login')
def Profile(request):
    user = request.user
    profile = user.companyprofile
    error = ""

    if request.method == 'POST':
        try:
            username = request.POST.get('UserName')
            email = request.POST.get('Email')
          
            company = request.POST.get('CompanyName')
            image = request.FILES.get('Profile')

            user.username = username
            user.email = email
          
            user.save()

            profile.company_name = company
            if image:
                profile.image = image
                
            profile.save()
            messages.info(request,"Profile Updated")
            return redirect('dashboard') 

        except Exception as e:
            error = str(e)

    return render(request, 'Shop/profile.html', {
        'user_data': user,
        'profile_data': profile,
        'error': error
    })



# Item List
@login_required(login_url='login')
def Items(request):
    user = request.user
   
    items = ItemMaster.objects.filter(profile_company_id=user.companyprofile)
    context = {
     
        'items': items,
    }
    return render(request, "Admin/Items.html", context)

# Add Item
@login_required(login_url='login')
def AddItem(request):
    user = request.user
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.profile_company_id = user.companyprofile
            new_item.save()
            messages.info(request,"Item Added")
            return redirect('items')
    else:
        form = ItemForm()

    return render(request, "Admin/AddItem.html", {'form': form})

# Edit Item
@login_required(login_url='login')
def EditItem(request, item_id):
    user = request.user
    item = get_object_or_404(ItemMaster, pk=item_id, profile_company_id=user.companyprofile)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.info(request,"Item Updated")
            return redirect('items')
    else:
        form = ItemForm(instance=item)

    return render(request, "Admin/EditItem.html", {'form': form, 'item': item})

# Delete Item
@login_required(login_url='login')
def DeleteItem(request, item_id):
    user = request.user
    item = get_object_or_404(ItemMaster, pk=item_id, profile_company_id=user.companyprofile)
    if request.method == 'POST':
        item.delete()
        return redirect('items')
    return render(request, "Admin/ConfirmDelete.html", {'item': item})

# Shop List
@login_required(login_url='login')
def Shops(request):
    user = request.user
    shops = ShopMaster.objects.filter(profile_company_id=user.companyprofile)
    return render(request, "Admin/Shops.html", {'shops': shops})

# Add Shop
@login_required(login_url='login')
def AddShop(request):
    user = request.user
    if request.method == 'POST':
        form = ShopForm(request.POST)
        if form.is_valid():
            new_shop = form.save(commit=False)
            new_shop.profile_company_id = user.companyprofile
            new_shop.save()
            messages.info(request,"Shop Added")
            return redirect('shops')
    else:
        form = ShopForm()
    return render(request, "Admin/AddShop.html", {'form': form})

# Edit Shop
@login_required(login_url='login')
def EditShop(request, shop_id):
    user = request.user
    shop = get_object_or_404(ShopMaster, pk=shop_id, profile_company_id=user.companyprofile)
    if request.method == 'POST':
        form = ShopForm(request.POST, instance=shop)
        if form.is_valid():
            form.save()
            messages.info(request,"Shop Updated")
            return redirect('shops')
    else:
        form = ShopForm(instance=shop)
    return render(request, "Admin/EditShop.html", {'form': form, 'shop': shop})

# Delete Shop
@login_required(login_url='login')
def DeleteShop(request, shop_id):
    user = request.user
    shop = get_object_or_404(ShopMaster, pk=shop_id, profile_company_id=user.companyprofile)
    if request.method == 'POST':    
        shop.delete()
        return redirect('shops')
    return render(request, "Admin/ConfirmDeleteShop.html", {'shop': shop})




# Shops name Api 
@require_GET
@login_required(login_url='login')
def get_shops(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    data = []
    if user.is_authenticated:

        data = ShopMaster.objects.filter(profile_company_id=user.companyprofile,active_status=True).values('id','name')
    return JsonResponse(list(data), safe=False)
# Item name Api
@require_GET
@login_required(login_url='login')
def get_items(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    data = []
    if user.is_authenticated:
        data = ItemMaster.objects.filter(profile_company_id=user.companyprofile,status=True).values('id', 'name')
    return JsonResponse(list(data), safe=False)






@require_GET
@login_required(login_url='login')
def kpi(request):
    user  = request.user
    if not user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    company = user.companyprofile


    today = datetime.today()
    month_start = today.replace(day=1)
    
    # Base Filter
    filters = {'shop__profile_company_id': company}


    # Stock Value 
    total_stock_value = InventorySummary.objects.filter(**filters).aggregate(Sum('stock_value'))['stock_value__sum'] or 0
    
    # Monthly Sales and profit
    monthly_sales_qs = SalesSummary.objects.filter(
        **filters, sale_date__gte=month_start
    ).aggregate(
        total_sales=Sum('total_amt'),
        total_profit=Sum('profit')
    )
    total_sales = monthly_sales_qs['total_sales'] or 0
    total_profit = monthly_sales_qs['total_profit'] or 0
    
    # Active Shops
    active_shops = ShopMaster.objects.filter(profile_company_id=company,active_status=True).aggregate(total=Count('id'))['total'] or 0

    data = {
        'total_stock_value': total_stock_value,
        'total_sales': total_sales,
        'total_profit': total_profit,
        'active_shops':active_shops
    } 
    return JsonResponse(data,safe=False)




@require_GET
@login_required(login_url='login')
def ChartApi(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    company  = user.companyprofile


    today = datetime.today()
    # Month Start
    month_start = str(date.today() - timedelta(days=30))
    


    #  Sales Trend Line Chart
    sales_trend = []
    for i in range(5,-1,-1):
        month =  (today - timedelta(days=i*30)).replace(day=1)
        month_str = month.strftime("%b %Y")
        sales = SalesSummary.objects.filter(shop__profile_company_id =  company,
                                            sale_date__year = month.year,
                                            sale_date__month = month.month
                                            ).aggregate(Sum('total_amt'))['total_amt__sum'] or  0
        sales_trend.append({'month':month_str,'sales':float(sales)})
    


    # Current and Previous Month    
    current_month = today.replace(day=1)
    previous_month = current_month - relativedelta(months=1)

    # Shop Sales Comparison Bar Chart
    current_month_sales = SalesSummary.objects.filter(
        shop__profile_company_id=company,
        sale_date__year=current_month.year,
        sale_date__month=current_month.month
    ).values('shop__name').annotate(total=Sum('total_amt')).order_by('shop__name')
    previous_month_sales = SalesSummary.objects.filter(
        shop__profile_company_id=company,
        sale_date__year=previous_month.year,
        sale_date__month=previous_month.month
    ).values('shop__name').annotate(total=Sum('total_amt')).order_by('shop__name')
    
    
    #  Payment Type by Shop (Stacked Bar)
    paymentype_type = SalesSummary.objects.filter(
    shop__profile_company_id=company,
    sale_date__year=month.year,
    sale_date__month=month.month
    ).values('shop__name', 'payment_type').annotate(
        total_pay=Sum('total_amt')
    ).order_by('shop__name', 'payment_type')

    #  Stock Value by Shop Chart
    stock_by_stock_values = InventorySummary.objects.filter(shop__profile_company_id =  company).values('shop__name').annotate(total=Sum('stock_value')).order_by('-total')


    # Top  5 sold items h bar
    top_items = SalesSummary.objects.filter(shop__profile_company_id =  company).values('item__name').annotate(total_qty=Sum('qty_sold')).order_by('-total_qty')[:5]
    
    # Top  5 profitable items h bar 
    top_items_profit = (
    SalesSummary.objects.filter(shop__profile_company_id =  company)
    .values('item__name')  
    .annotate(
        total_profit=Sum('profit'),
        total_sold=Sum('qty_sold'),
        total_sales=Sum('total_amt'),
        margin_percent=ExpressionWrapper(
            100 * Sum('profit') / Sum('total_amt'),
            output_field=FloatField()
        )
    )
    .order_by('-margin_percent')[:5]  
    )

    # Shop wise Profit    
    shop_profit = SalesSummary.objects.filter(sale_date__gte=month_start,shop__profile_company_id =  company).values('shop__name').annotate(
    total_profit=Sum('profit')
    ).order_by('-total_profit')
    
    # Shop Wise  Stock Available Qty
    stock_by_stock_available_qty = InventorySummary.objects.filter(shop__profile_company_id =  company).values('shop__name').annotate(total=Sum('available_qty')).order_by('-total')
    
   
    return JsonResponse( {
                          'sales_trend':list(sales_trend),

                          'previous_month_sales': list(previous_month_sales),
                          'shop_sales': list(current_month_sales),
                          
                          'paymentype_type':list(paymentype_type),
                          'stock_by_stock_values':list(stock_by_stock_values),
                          
                          'shop_profit':list(shop_profit),
                          'top_items_profit':list(top_items_profit),
                          'top_items':list(top_items), 
                          'stock_by_stock_available_qty':list(stock_by_stock_available_qty)
                          }
   ,safe=False)



@require_GET
@login_required(login_url='login')
def Table(request): 
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    company  = user.companyprofile

    #  Sold Items Table
    top_items = SalesSummary.objects.filter(shop__profile_company_id =  company).values('item__name').annotate(total_qty=Sum('qty_sold')).order_by('-total_qty')[:5]

    # Top Profit Table
    top_items_profit = (
    SalesSummary.objects.filter(shop__profile_company_id =  company)
    .values('item__name')  
    .annotate(
        total_profit=Sum('profit'),
        total_sold=Sum('qty_sold'),
        total_sales=Sum('total_amt'),
        margin_percent=ExpressionWrapper(
            100 * Sum('profit') / Sum('total_amt'),
            output_field=FloatField()
        )
    )
    .order_by('-total_profit')[:5]  
    )

    # Recent Sales Table
    recent_sales = SalesSummary.objects.filter(
        shop__profile_company_id=company
    ).values(
        'invoice_no',
        'shop__name',
        'item__name',
        'qty_sold',
        'sale_date',
        'total_amt'
    ).order_by('-sale_date')[:5]

    
    # Recent Purchases Table
    recent_receive = ReceiveLog.objects.filter(shop__profile_company_id=company).values('shop__name','item__name','qty','rate','date').order_by('-date')[:5]

    # Low Stock Table
    low_stock = InventorySummary.objects.filter(shop__profile_company_id=company,available_qty__lte=10).values('item__name', 'available_qty').order_by('available_qty')[:5]

   
    
  
    return JsonResponse({
        'top_items':list(top_items),
        'top_items_profit':list(top_items_profit),
        'recent_sales':list(recent_sales),
        'recent_receive':list(recent_receive),
        'low_stock':list(low_stock)
        }
        ,safe=False)

# Home Dashboard
@login_required(login_url='login')
def Dashboard(request):
    
    return render(request, 'Dashboard/Dashboard.html')


# Inventroy Dashboard
@login_required(login_url='login')
def Inventroy(request):
    user = request.user
    company = user.companyprofile

    # Shops and Items Filter for dropdown
    shops = ShopMaster.objects.filter(active_status=True, profile_company_id=company)
    items = ItemMaster.objects.filter(status=True, profile_company_id=company)
    
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
    low_stock = summaries.filter(available_qty__lt=10)


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



    context = {
        'shops': shops,
        'items': items,

        'selected_shop': shop_filter,
        'selected_item': item_filter,
    

        'shop_summary': shop_summary,
        'item_data':item_data,
        'low_stock': low_stock
    }
    return render(request, 'Dashboard/Inventroy.html',context)


# Receive Dashboard
@login_required(login_url='login')
def Receive(request):
    user = request.user
    company = user.companyprofile

    # Filters 
    from_date = request.GET.get('from_date') or str(date.today() - timedelta(days=30))
    to_date = request.GET.get('to_date') or str(date.today())
    shop_filter = request.GET.get('shop')
    item_filter = request.GET.get('item')

    # Shops and Items Filter for dropdown
    shops = ShopMaster.objects.filter(active_status=True, profile_company_id=company)
    items = ItemMaster.objects.filter(status=True, profile_company_id=company)

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

    context = {
        'shops': shops,
        'items': items,
        
        'selected_shop': shop_filter,
        'selected_item': item_filter,
        'from_date': from_date,
        'to_date': to_date,

        'shop_summary': shop_summary,
        'item_data': item_data,
        'receives':receives_qs.order_by('-date')


    }
    return render(request, 'Dashboard/Receive.html', context)




# Sales Dashboard
@login_required(login_url='login')
def Sales(request):
    user = request.user
    company = user.companyprofile
    
    # Shops and Items Filter for dropdown
    shops = ShopMaster.objects.filter(active_status=True, profile_company_id=company)
    items = ItemMaster.objects.filter(status=True, profile_company_id=company)

  
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
    ).order_by('-total_qty')[:5]


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
   
    context = {
        'shops': shops,
        'items': items,

        'selected_shop': shop_filter,
        'selected_item': item_filter,
        'selected_payment':payment_type_filter,
        'from_date': from_date,
        'to_date': to_date,
        
        'date_data': date_data,
        'revenue_data': revenue_data,
        'payment_data':payment_data,
        'top_items': top_items,
        'sales':sales_qs.order_by('-sale_date')
       
    }
    return render(request, 'Dashboard/Sales.html', context)

# Profitability Dashboard
@login_required(login_url='login')
def Profitability(request):
    user = request.user
    company = user.companyprofile

    # Shops and items name for dropdown    
    shops = ShopMaster.objects.filter(active_status=True, profile_company_id=company)
    items = ItemMaster.objects.filter(status=True, profile_company_id=company)

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

    context = {
        'shops': shops,
        'items': items,
        

        'selected_shop': shop_filter,
        'selected_item': item_filter,
        'selected_payment':payment_type_filter,
        'from_date': from_date,
        'to_date': to_date,
        
        'shop_profit': shop_profit,
        'item_profit': item_profit,
      
        
    }
    return render(request, 'Dashboard/Profitability.html', context)



