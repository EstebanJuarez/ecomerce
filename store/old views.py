from django.shortcuts import render
from numpy import product
from .models import * ## pongo el.model porq model está en la misma carpeta
from django.http import JsonResponse
import datetime
import json

##este views est antes de optimizar codigo

# Create your views here.
def store(request):
    if request.user.is_authenticated:
        customer=request.user.customer
        order, created= Order.objects.get_or_create(customer=customer, completed=False)##aqui creamos la orden para que funcione el store admeas para que caundo terminemos la orden se cree otra
        items= order.orderitem_set.all() ##gracias a que son order es padre puede acceder al ortder item
        cartItems=order.get_cart_items
    else:
        ##le mandamos todo los datos vacios porq si el valor de context diccionary esta vacio y lo renderiza da error
        items=[]
        order ={'get_cart_total':0, 'get_cart_items':0,'shipping':False}
        cartItems= order['get_cart_items']

    products= Product.objects.all()
    context={'products':products,'cartItems':cartItems}
    return render(request, 'store/store.html',context)

def cart(request):

    if request.user.is_authenticated:
        customer=request.user.customer
        order, created= Order.objects.get_or_create(customer=customer, completed=False)
        items= order.orderitem_set.all() ##gracias a que son order es padre puede acceder al ortder item
        cartItems=order.get_cart_items
        
    else:
        ##le mandamos todo los datos vacios porq si el valor de context diccionary esta vacio y lo renderiza da error. actualizacion: una vez creadas las cookies ya no mandamos estos datos  vacios, mandamos los valores guardados en la cookie
        ## le mandamos el valor de las cookies usamos el json.loads pra que lo guarde en un diccionario de pytonh
        try:            
            cart= json.loads(request.COOKIES['cart'])
            print ("cart", cart)
        except:
            cart ={} ## le madnamos vacio por si no detecta la cookie, esto pasa si abre la pagina cart directamente por primera vez
        items=[]
        order ={'get_cart_total':0, 'get_cart_items':0 ,'shipping':False}
        cartItems= order['get_cart_items']

        for i in cart:

            ## encerramos todos en un try catch porq si el usuario anonimo añade un producto al carro y luego este producto lo borramos en la base de datos le saltará un error
            try:

                cartItems += cart[i]["quantity"]

                product = Product.objects.get(id = i) ## lo querriamos al product, ahora podemos acceder al product ya que tenemos su id

                total = (product.price * cart[i]["quantity"] )

                order['get_cart_total'] += total
                order['get_cart_items'] +=  cart[i]["quantity"]

                ## aqui creamos el diccionario y le damos los valores de la forma igual que en <div style="flex:2;">{{item.product.name}}</div> cart.html para que no tengamos que cambiar el codigo de ahí
                item ={
                    'product':{
                        'id':product.id,
                        'name':product.name,
                        'price':product.price,
                        'imageURL':product.imageURL,
                        },
                        'quantity':cart[i]['quantity'],
                        'get_total':total,
                        }
                items.append(item)

                if product.digital == False:
                    order['shipping'] = True
            except:
                pass
    context={'items':items, 'order': order,'cartItems':cartItems }
    return render(request, 'store/cart.html',context)

def checkout(request):

    if request.user.is_authenticated:
        customer=request.user.customer
        order, created= Order.objects.get_or_create(customer=customer, completed=False)
        items= order.orderitem_set.all() ##gracias a que son order es padre puede acceder al ortder item
        cartItems=order.get_cart_items
    else:
        ##le mandamos todo los datos vacios porq si el valor de context diccionary esta vacio y lo renderiza da error
        items=[]
        order ={'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems= order['get_cart_items']

    context={'items':items, 'order': order,'cartItems':cartItems}

    return render(request, 'store/checkout.html', context)

def updateItem(request):
    ##Aqui recibimos lo que mandamos del cart.js en la parte de body:JSON etc
    data = json.loads(request.body)
    productId=data['productId']
    action =data ['action']

    print(action)
    print(productId)

    customer= request.user.customer
    product= Product.objects.get(id=productId)
    order, created= Order.objects.get_or_create(customer=customer, completed=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)#si estea orderden y con este producto ya existe solamente queremos añadirle o quitarle, pero no crear otra
    #por eso se usa el get or create

    if action =='add':
        orderItem.quantity =(orderItem.quantity + 1)
    elif action=='remove':
        orderItem.quantity= (orderItem.quantity - 1)

    orderItem.save()
    if orderItem.quantity <=0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    ##aqui recibimos el dato del checkout.html linea 134 en adelante hasta la 141 aprox y devolvemos esto que está aqui
    transaction_id = datetime.datetime.now().timestamp()

    ##aqui guardamos lo que recibimos dentro de data
    data = json.loads(request.body)


    if request.user.is_authenticated:
        customer = request.user.customer
        order, created= Order.objects.get_or_create(customer=customer, completed=False)
        total = float(data['form']['total'])##aqui elegimos a cual queremos acceder 
        order.transaction_id=transaction_id ## aqui le madnamos a la base de datos el valor de la ide de la orden

        if total == float(order.get_cart_total):## aqui cmprobamos si los totales conciden para hacer que la orden se de por terminada y para que la persona no pueda manipular el frontend y compre algo al precio de 0
            order.completed=True

        order.save() ## lo gaurdamos igual haya o no manipulado el usuario el frontend, pero si la orden no está completa es porque si lo manipularon

            ## ahora si shipping es true le damos todos los valores obtenidos en js a la base de datos
        if order.shipping ==True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )
    else:
        print ("El usuario no está logueado")
    return JsonResponse('Pago completado', safe=False)
