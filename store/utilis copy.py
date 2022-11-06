import json
from .models import *


def cookieCart(request):
     # le mandamos todo los datos vacios porq si el valor de context diccionary esta vacio y lo renderiza da error. actualizacion: una vez creadas las cookies ya no mandamos estos datos  vacios, mandamos los valores guardados en la cookie
        # le mandamos el valor de las cookies usamos el json.loads pra que lo guarde en un diccionario de pytonh
    try:
        cart = json.loads(request.COOKIES['cart'])
        print("cart", cart)
    except:
        cart = {}  # le madnamos vacio por si no detecta la cookie, esto pasa si abre la pagina cart directamente por primera vez
    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = order['get_cart_items']

    for i in cart:

        # encerramos todos en un try catch porq si el usuario anonimo añade un producto al carro y luego este producto lo borramos en la base de datos le saltará un error
        try:

            cartItems += cart[i]["quantity"]

            # lo querriamos al product, ahora podemos acceder al product ya que tenemos su id
            product = Product.objects.get(id=i)

            total = (product.price * cart[i]["quantity"])

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]["quantity"]

            # aqui creamos el diccionario y le damos los valores de la forma igual que en <div style="flex:2;">{{item.product.name}}</div> cart.html para que no tengamos que cambiar el codigo de ahí
            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL,
                    },
                    'quantity': cart[i]['quantity'],
                    'get_total': total,
                    }
            items.append(item)

            if product.digital == False:
                order['shipping'] = True
        except:
            pass
    return {'cartItems':cartItems,'order':order, 'items':items}

def cartData(request):
    if request.user.is_authenticated:
        customer=request.user.customer
        order, created= Order.objects.get_or_create(customer=customer, completed=False)
        items= order.orderitem_set.all() ##gracias a que son order es padre puede acceder al ortder item
        cartItems=order.get_cart_items
    else:
        cookieData= cookieCart(request) ## guardo todo lo de cookiecart aquí entonces depues puedo acceder a todos los datos de cookie cart 
        cartItems= cookieData['cartItems']
        order= cookieData['order']
        items= cookieData['items']

    return {'cartItems':cartItems,'order':order, 'items':items}

def guestOrder(request, data):
    print ("El usuario no está logueado")
    print ("cookies", request.COOKIES)

    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(
        email = email,
    )
    customer.name = name ## el name lo ponemos fuera porq si la persona quiere vovler a usar el mismo email pero otro nombre puede

    customer.save ()

    order = Order.objects.create (
        customer=customer,
        complete = False,
    )

    for item in items :
        product = Product.objects.get(id =item['product']['id']) ## esto se conecta con utilis.py  linea 33 donde creamos  el diccionario y decimos que dentro de product está id con el valor de produc.id

        orderItem=OrderItem.objects.create(
            product = product,
            order =order,
            quantity = item['quantity'] ## esta tambien la sacamos del utilis.py linea 33 /40

        )

    return customer, order