from datetime import datetime

from django.shortcuts import render
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserProfileForm
from rango.webhose_search import run_query

from registration.backends.simple.views import RegistrationView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login


def index(request):
    # request.session.set_test_cookie()
    # return HttpResponse("Rango says hey there partner! <br/><a href='/rango/about/'>About</a>")
    category_list = Category.objects.order_by('-likes')[:5]  # 负号表示取倒序
    page_list = Page.objects.order_by('-views')[:5]  # 5个访问最多的网页
    context_dict = {'categories': category_list, 'pages': page_list}

    # 调用处理cookie的辅助函数
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']

    response = render(request, 'rango/index.html', context_dict)
    return response


def about(request):
    # if request.session.test_cookie_worked():
    #     print("Test Cookie Worked!")
    #     request.session.delete_test_cookie()
    visitor_cookie_handler(request)
    context_dict = {'name': "Hython", 'visits': request.session['visits']}
    # return HttpResponse("<html><h2>this is about page...</h2><br/><a href='/rango/'>Index</a></html>")
    return render(request, 'rango/about.html', context=context_dict)


def show_category(request, category_name_slug):
    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category).order_by('-views')   # 按访问次数排序网页
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    # search
    # 设定一个默认的搜索词条（分类名），显示在搜索框中
    context_dict['query'] = category.name

    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            # 调用前面定义的函数向 Webhose 发起查询，获得结果列表
            result_list = run_query(query)
            context_dict['query'] = query
            context_dict['result_list'] = result_list

    return render(request, 'rango/category.html', context_dict)


@login_required
def add_category(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=True)
            print(category, category.slug)
            return index(request)
        else:   # 表单数据有错误 直接在终端里打印出来
            print(form.errors)
    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
            return show_category(request, category_name_slug)
        else:
            print(form.errors)
    else:
        form = PageForm()
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)


@login_required
def register_profile(request):
    form = UserProfileForm()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            return redirect('index')
        else:
            print(form.errors)
    context_dict = {'form': form}
    return render(request, 'rango/profile_registration.html', context_dict)

# def register(request):
#     # 一个布尔值，告诉模板注册是否成功
#     # 一开始设为 False，注册成功后改为 True
#     registered = False
#     # 如果是 HTTP POST 请求，处理表单数据
#     if request.method == 'POST':
#         user_form = UserForm(data=request.POST)
#         profile_form = UserProfileForm(data=request.POST)
#         if user_form.is_valid() and profile_form.is_valid():
#             user = user_form.save()
#             # 使用 set_password 方法计算密码哈希值
#             # 然后更新 user 对象
#             user.set_password(user.password)
#             user.save()
#
#             # 现在处理 UserProfile 实例
#             # 因为要自行处理 user 属性，所以设定 commit=False
#             # 延迟保存模型，以防出现完整性问题
#             profile = profile_form.save(commit=False)
#             profile.user = user
#             # 如果用户提供了头像，从表单数据库中提取出来，赋给 UserProfile 模型
#             if 'picture' in request.FILES:
#                 profile.picture = request.FILES['picture']
#             # 保存 UserProfile 模型实例
#             profile.save()
#             # 更新变量的值，告诉模板成功注册了
#             registered = True
#         else:
#             # 表单数据无效，出错了？
#             print(user_form.errors, profile_form.errors)
#     else:
#         user_form = UserForm()
#         profile_form = UserProfileForm()
#     # 根据上下文渲染模板
#     return render(request, 'rango/register.html',
#                   {'user_form': user_form,
#                    'profile_form': profile_form,
#                    'registered': registered})
#
#
# def user_login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(username=username, password=password)
#         if user:
#             if user.is_active:
#                 # 登入有效且已激活的账户
#                 # 然后重定向到首页
#                 login(request, user)
#                 return HttpResponseRedirect(reverse('index'))
#             else:
#                 # 账户未激活，禁止登录
#                 return HttpResponse('Your Rango account is disabled.')
#         else:
#             # 提供的登录凭据有问题，不能登录
#             print("Invalid login details: {0}, {1}".format(username, password))
#             return HttpResponse("Invalid login details supplied.")
#     # 不是 HTTP POST 请求，显示登录表单
#     # 极有可能是 HTTP GET 请求
#     else:
#         # 没什么上下文变量要传给模板系统
#         # 因此传入一个空字典
#         return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
    content = "Since you're logged in, you can see this text!"
    return render(request, 'rango/restricted.html', {'context': content})


# 只有已登录的用户才能访问这个视图
# @login_required
# def user_logout(request):
#     # 可以确定用户已登录，因此直接退出
#     logout(request)
#     # 把用户带回首页
#     return HttpResponseRedirect(reverse('index'))


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):
    # 从服务端获取cookie
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
    # 如果距上次访问已超过一天
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # 增加访问次数后更新“last_visit”cookie
        request.session['last_visit'] = str(datetime.now())
    else:
        # 设定“last_visit”cookie
        request.session['last_visit'] = last_visit_cookie
    # 更新或设定“visits”cookie
    request.session['visits'] = visits


def search(request):
    result_list = []
    query = ''
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            # 调用前面定义的函数向 Webhose 发起查询，获得结果列表
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list, 'query': query})


# 记录网页的访问次数
def track_url(request):
    page_id = None
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
    if page_id:
        try:
            page = Page.objects.get(id=page_id)
            page.views = page.views + 1
            page.save()
            return redirect(page.url)
        except:
            return HttpResponse("Page id {0} not found".format(page_id))
    print("No page_id in get string")
    return redirect(reverse('index'))


# 用户成功注册后重定向到首页
class RangoRegistrationView(RegistrationView):
    def get_success_url(self, user):
        return reverse('register_profile')


# 个人资料编辑
@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('index')

    userprofile = UserProfile.objects.get_or_create(user=user)[0]
    # 创建form实例
    form = UserProfileForm({'website': userprofile.website, 'picture': userprofile.picture})

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save(commit=True)
            return redirect('profile', user.username)
        else:
            print(form.errors)

    return render(request, 'rango/profile.html', {'userprofile': userprofile, 'selecteduser': user, 'form': form})


# 列出用户资料
@login_required
def list_profiles(request):
    userprofile_list = UserProfile.objects.all()
    return render(request, 'rango/list_profiles.html', {'userprofile_list': userprofile_list})


# 点赞
@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
    likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes = likes
            cat.save()
    return HttpResponse(likes)


# 使用过滤器查找以指定字符串开头的分类
def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)

        if max_results > 0:
            if len(cat_list) > max_results:
                cat_list = cat_list[:max_results]
    return cat_list


def suggest_category(request):
    cat_list = []
    starts_with = ''

    if request.method == 'GET':
        starts_with = request.GET['suggestion']
    cat_list = get_category_list(8, starts_with)
    return render(request, 'rango/cats.html', {'cats': cat_list})
