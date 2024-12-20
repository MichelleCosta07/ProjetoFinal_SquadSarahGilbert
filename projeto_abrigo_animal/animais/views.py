from django.shortcuts import render, get_object_or_404
from animais.forms import AnimalForm,AdocaoForm
from .models import Animal
from django.http import HttpResponseRedirect
import folium
import requests
#from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

# ----------------------------------------------------------------------- HOME

from django.shortcuts import render
from django.views.decorators.cache import never_cache
from .forms import AnimalForm
from .models import Animal

@never_cache  # Desativa o cache da view
def home(request):
    form = AnimalForm()  
    animais = Animal.objects.all()  

    # Se algum parâmetro GET é passado, aplica os filtros
    if request.method == "GET":
        nome_pet = request.GET.get('nome_pet', '')
        tipo = request.GET.get('tipo', '')
        sexo = request.GET.get('sexo', '')
        porte = request.GET.get('porte', '')
        estado = request.GET.get('estado', '')
        cidade = request.GET.get('cidade', '')

        pagina = request.GET.get("pagina",1)

        # Filtrando os animais com base nos critérios fornecidos
        if nome_pet:
            animais = animais.filter(nome__icontains=nome_pet)
        if tipo:
            animais = animais.filter(tipo=tipo)
        if sexo:
            animais = animais.filter(sexo=sexo)
        if porte:
            animais = animais.filter(porte=porte)
        if estado:
            animais = animais.filter(estado=estado)
        if cidade:
            animais = animais.filter(cidade=cidade)

        num_animais_pag = 6
        paginator = Paginator(animais, num_animais_pag)

    # Renderiza a página com o formulário e a lista filtrada
    return render(request, 'home.html', {
        'url': request.path_info,
        'animais': paginator.get_page(pagina), 
        'form': form,
        'nome_pet': nome_pet,
        'tipo': tipo,
        'sexo': sexo,
        'porte': porte,
        'estado': estado,
        'cidade': cidade,
    })





# ----------------------------------------------------------------------- MAP

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
import ipaddress

def get_client_ipv4(request):
    ip = get_client_ip(request)
    
    # Validate if it's an IPv4 address
    try:
        ip_obj = ipaddress.ip_address(ip)
        if isinstance(ip_obj, ipaddress.IPv4Address):
            return str(ip_obj)  # Return only IPv4 address as a string
        else:
            return None  # If it's an IPv6, return None or handle it differently
    except ValueError:
        return None  # In case the IP is invalid or not parsable

def get_geolocation(ip_address):
    #ip_address = 'your_ip_address'  # Use 'your_ip_address' or 'check' for your current IP
    url = f'http://ip-api.com/json/{ip_address}'

    response = requests.get(url)
    data = response.json()

    print(data)

    latitude = data['lat']
    longitude = data['lon']

    return latitude, longitude

def map_view(request, lat=-23.9613 ,lon=-46.391):
    mapa = folium.Map(location=[-22.449, -48.6388], zoom_start=6.5) # location starter
    folium.Marker(location=[-21.1775000, -47], icon=folium.Icon(popup="Star Icon",color='purple')).add_to(mapa)
    folium.Marker(location=[float(lat), float(lon)], icon=folium.Icon(color='orange')).add_to(mapa)
    mapa.save('animais/templates/map.html')
    return render(request, 'map.html')

# ----------------------------------------------------------------------- DETALHES

#@login_required
def detalhes(request, id): # 
    print(request)
    ip = get_client_ip(request)
    ip = '177.100.236.65'
    lat, lon = get_geolocation(ip)

    animal = get_object_or_404(Animal, id=id)  # Ou use outro campo único
    animais = Animal.objects.all()  # Recupera todos os animais para a galeria
    map_view(request, lat, lon)
    return render(request, 'detalhes.html', {'animal': animal, 'animais': animais})





# ----------------------------------------------------------------------- CADASTRO ANIMAL

#@login_required
def cadastro_animal(request):
     if request.method == 'POST':
      form = AnimalForm(request.POST, request.FILES)  # Cria uma instância do formulário 
      if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
     else :
        form = AnimalForm()  # Cria uma instância do formulário
        return render(request, 'cadastro_animal.html',{'form': form})
     
# ----------------------------------------------------------------------- CADASTRO ANIMAL

def solicitacao_adocao(request, id):
    animal = get_object_or_404(Animal, id=id)  # Obtém o animal pelo ID

    if request.method == 'POST':
        form = AdocaoForm(request.POST, request.FILES)
        if form.is_valid():
            adocao = form.save(commit=False)  # Não salva ainda
            adocao.animal = animal  # Associa o animal à adoção
            adocao.user = request.user  # Associa o usuário à adoção
            adocao.save()  # Agora salva
    else:
        form = AdocaoForm()

    return render(request, 'solicitacao_adocao.html', {'form': form, 'animal': animal})


# ----------------------------------------------------------------------- LIVIA


def quero_ajudar(request):
    return render(request, 'quero_ajudar.html')

def sobre_nos(request):
    return render(request, 'sobre_nos.html')


