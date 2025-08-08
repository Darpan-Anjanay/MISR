async function kpi() {
    try {
      
        const response = await fetch('/api/kpi/');
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
            }
        const data = await response.json();
        
        document.querySelector('#total_stock_value').textContent = `₹ ${data.total_stock_value ?? 0}`;
        document.querySelector('#total_sales').textContent = `₹ ${data.total_sales ?? 0}`;
        document.querySelector('#total_profit').textContent = `₹ ${data.total_profit ?? 0}`;
        document.querySelector('#active_shops').textContent = data.active_shops ?? 0;
        
        


    } catch (error) {
        console.error('Error:', error);
    } 
}
kpi();

async function salestrend() {
    try {
        const response = await fetch('/api/chartapi/');
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const {
            sales_trend,
            previous_month_sales,
            shop_sales,
            paymentype_type,
            stock_by_stock_values,
            top_items,
            top_items_profit,
            shop_profit,
            stock_by_stock_available_qty
        } = await response.json();


        // Chart  generator
        const createChart = (
                        ctxId,
                        chartType,
                        labels,
                        datasets,
                        { format = 'currency', horizontal = false } = {}
                    ) => {
                        const ctx = document.getElementById(ctxId)?.getContext('2d');
                        if (!ctx) throw new Error(`${ctxId} canvas not found`);

                        const formatValue = value => {
                            return format === 'currency'
                                ? `₹${value.toLocaleString('en-IN')}`
                                : value.toLocaleString('en-IN');
                        };

                        const options = {
                            responsive: true,
                            plugins: {
                                legend: {
                                    display: true,
                                    position: 'bottom'
                                },
                                tooltip: {
                                    callbacks: {
                                        label: function(context) {
                                                                    const value = context.raw ?? context.parsed.y ?? context.parsed.x;
                                                                    return `${context.dataset.label || ''}: ${formatValue(value)}`;
                                                                }
                                                }
                                        }
                                    }
                                        };

   
                        if (!['pie', 'doughnut'].includes(chartType)) {
                            options.indexAxis = horizontal ? 'y' : 'x';
                            options.scales = {
                                [horizontal ? 'x' : 'y']: {
                                    beginAtZero: true,
                                    ticks: {
                                        callback: formatValue
                                    }
                                }
                            };
                        }

                        new Chart(ctx, {
                            type: chartType,
                            data: {
                                labels,
                                datasets
                            },
                            options
                        });
};


        // Sales Trend Line Chart
        createChart(
            'salesTrendChart',
            'line',
            sales_trend.map(item => item.month),
            [{
                label: 'Monthly Sales',
                data: sales_trend.map(item => item.sales),
                backgroundColor: 'rgba(54, 162, 235, 0.4)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        );

        // Shop Sales Comparison Bar Chart
        const shopLabels = shop_sales.map(item => item.shop__name);
        const currentMonthMap = new Map(shop_sales.map(item => [item.shop__name, item.total]));
        const previousMonthMap = new Map(previous_month_sales.map(item => [item.shop__name, item.total]));

        createChart(
            'shopSalesChart',
            'bar',
            shopLabels,
            [
                {
                    label: 'Previous Month',
                    data: shopLabels.map(label => previousMonthMap.get(label) || 0),
                    backgroundColor: 'rgba(255, 99, 132, 0.4)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                    barThickness: 20
                },
                {
                    label: 'Current Month',
                    data: shopLabels.map(label => currentMonthMap.get(label) || 0),
                    backgroundColor: 'rgba(54, 162, 235, 0.4)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    barThickness: 20
                }
            ]
        );

        
        // Payment Type by Shop (Stacked Bar)
        const shopNames = [...new Set(paymentype_type.map(item => item['shop__name']))];
        const paymentTypes = [...new Set(paymentype_type.map(item => item.payment_type))];
        const paymentColors = ['rgba(54, 162, 235, 0.4)', 'rgba(255, 99, 132, 0.4)', 'rgba(128, 243, 61, 0.6)'];

        const paymentDatasets = paymentTypes.map((type, index) => ({
            label: type,
            data: shopNames.map(shop =>
                (paymentype_type.find(item => item['shop__name'] === shop && item.payment_type === type)?.total_pay || 0)
            ),
            backgroundColor: paymentColors[index % paymentColors.length],
            barThickness: 20
        }));

        createChart(
            'PaymentTypeChart',
            'bar',
            shopNames,
            paymentDatasets
        );

        // Stock Value by Shop Chart bar 
        createChart(
            'stockvaluebyshopChart',
            'bar',
            stock_by_stock_values.map(item => item.shop__name),
            [{
                label: 'Stock Value By Shops',
                data: stock_by_stock_values.map(item => item.total),
                backgroundColor: 'rgba(54, 162, 235, 0.4)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 0.4,
                barThickness: 20
            }]
        );

        // Top 5 Sold Items H bar
      
        createChart(
            'topsolditems',
            'bar',
            top_items.map(item => item.item__name),
            [{
                label: 'Top 5 Sold Items',
                data: top_items.map(item => item.total_qty),
                backgroundColor: 'rgba(54, 162, 235, 0.4)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 0.4,
                barThickness: 20
            }],
            { format: 'quantity', horizontal: true }  
        );


        // Top 5 Sold Items By profit H bar
      
        createChart(
            'topsoldbyprofit',
            'bar',
            top_items_profit.map(item => item.item__name),
            [{
                label: 'Top 5 Sold Items Margin %',
                data: top_items_profit.map(item => item.margin_percent),
                backgroundColor: 'rgba(54, 162, 235, 0.4)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 0.4,
                barThickness: 20
            }],
            {  format: 'quantity',horizontal: true }  
        );
       
        // Shop wise Profit Pie Chart
        createChart(
            'shopwiseprofit',
            'pie',
            shop_profit.map(item => item.shop__name),  
            [{
                label: 'Shop-wise Profit',
                data: shop_profit.map(item => item.total_profit),
                backgroundColor: [
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(255, 206, 86, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(153, 102, 255, 0.6)',
                    'rgba(255, 159, 64, 0.6)'
                ],
                borderColor: 'white',
                borderWidth: 1
            }],
            { format: 'currency' }  
        );


        // Shop Wise  Stock Available Qty Pie Chart    
        createChart(
            'stockquantity',
            'pie',
            stock_by_stock_available_qty.map(item => item.shop__name),
            [{
                label: 'Stock By Quantity',
                data: stock_by_stock_available_qty.map(item => item.total),
                backgroundColor: [
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(255, 206, 86, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(153, 102, 255, 0.6)',
                    'rgba(255, 159, 64, 0.6)'
                ],
                borderColor: 'white',
                borderWidth: 1
            }],
            { format: 'quantity' } 
        );




    } catch (error) {
        console.error('Error:', error);
    }
}

salestrend();



async function Tables() {
    try {
        const response = await fetch('/api/table/');
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        const { top_items, top_items_profit, recent_sales, recent_receive, low_stock } = data;

        // ---------- Sold Items Table ----------
        const sold_items_table = document.getElementById('sold_items_table');
        if (sold_items_table && Array.isArray(top_items)) {
            let tableHTML = `
                <thead class="table-light">
                    <tr>
                        <th>Item Name</th>
                        <th>Total Quantity</th>
                    </tr>
                </thead>
                <tbody>
            `;

            top_items.forEach(it => {
                tableHTML += `
                    <tr>
                        <td>${it.item__name}</td>
                        <td>${it.total_qty}</td>
                    </tr>
                `;
            });

            tableHTML += `</tbody>`;
            sold_items_table.innerHTML = tableHTML;
        }

        // ---------- Top Profit Table ----------
        const profit_table = document.getElementById('profit_table');
        if (profit_table && Array.isArray(top_items_profit)) {
            let tableHTML = `
                <thead class="table-light">
                    <tr>
                        <th>Item Name</th>
                        <th>Total Profit</th>
                        <th>Total Sold</th>
                        <th>Total Sales</th>
                        <th>Margin %</th>
                    </tr>
                </thead>
                <tbody>
            `;
            top_items_profit.forEach(it => {
                tableHTML += `
                    <tr>
                        <td>${it.item__name}</td>
                        <td>${it.total_profit}</td>
                        <td>${it.total_sold}</td>
                        <td>${it.total_sales}</td>
                        <td>${it.margin_percent}</td>
                    </tr>
                `;
            });
            tableHTML += `</tbody>`;
            profit_table.innerHTML = tableHTML;
        }

        // ---------- Recent Sales Table ----------
        const recent_sales_table = document.getElementById('recentsales_table');
        if (recent_sales_table && Array.isArray(recent_sales)) {
            let tableHTML = `
                <thead class="table-light">
                    <tr>
                        <th>Invoice</th>
                        <th>Shop</th>
                        <th>Item</th>
                        <th>Qty</th>
                        <th>Amount</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
            `;
            recent_sales.forEach(sale => {
            const dateObj = new Date(sale.sale_date);
            const day = String(dateObj.getDate()).padStart(2, '0');
            const month = String(dateObj.getMonth() + 1).padStart(2, '0'); 
            const year = dateObj.getFullYear();
            const formattedDate = `${day}-${month}-${year}`;

            tableHTML += `
                <tr>
                    <td>${sale.invoice_no}</td>
                    <td>${sale.shop__name}</td>
                    <td>${sale.item__name}</td>
                    <td>${sale.qty_sold}</td>
                    <td>₹${sale.total_amt}</td>
                    <td>${formattedDate}</td>
                </tr>
            `;
            });
            tableHTML += `</tbody>`;
            recent_sales_table.innerHTML = tableHTML;
        }

        // ---------- Recent Purchases Table ----------
        const purchases_table = document.getElementById('recent_purchases_table');
        if (purchases_table && Array.isArray(recent_receive)) {
            
            let tableHTML = `
                <thead class="table-light">
                    <tr>
                        <th>Shop</th>
                        <th>Item</th>
                        <th>Qty</th>
                        <th>Rate</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
            `;
            recent_receive.forEach(entry => {
                const dateObj = new Date(entry.date);
                const day = String(dateObj.getDate()).padStart(2, '0');
                const month = String(dateObj.getMonth() + 1).padStart(2, '0'); 
                const year = dateObj.getFullYear();
                const formattedDate = `${day}-${month}-${year}`;   
                
                tableHTML += `
                    <tr>
                        <td>${entry.shop__name}</td>
                        <td>${entry.item__name}</td>
                        <td>${entry.qty}</td>
                        <td>₹${entry.rate}</td>
                        <td>${formattedDate}</td>  
                    </tr>
                `;
            });
            tableHTML += `</tbody>`;
            purchases_table.innerHTML = tableHTML;
        }

        // ---------- Low Stock Table ----------
        const low_stock_table = document.getElementById('low_stock_items_table');
        if (low_stock_table && Array.isArray(low_stock)) {
            let tableHTML = `
                <thead class="table-light">
                    <tr>
                        <th>Item</th>
                        <th>Available Qty</th>
                    </tr>
                </thead>
                <tbody>
            `;
            low_stock.forEach(item => {
                tableHTML += `
                    <tr>
                        <td>${item.item__name}</td>
                        <td>${item.available_qty}</td>
                    </tr>
                `;
            });
            tableHTML += `</tbody>`;
            low_stock_table.innerHTML = tableHTML;
        }

    } catch (error) {
        console.error('Error loading table data:', error);
    }
}

Tables();
