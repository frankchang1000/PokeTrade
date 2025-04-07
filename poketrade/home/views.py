from django.shortcuts import render

def index(request):
    template_data = {}
    template_data['title'] = 'PokeTrade'
    
    if request.user.is_authenticated:
        template_data['greeting'] = f'Welcome, {request.user.username}!'
    
    return render(request, 'home/index.html', {'template_data': template_data})

def about(request):
    template_data = {}
    template_data['title'] = 'About'
    return render(request, 'home/about.html', {'template_data': template_data})