from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django_recaptcha.fields import ReCaptchaField

class CountryForm(forms.Form):
    choose_country = [
        ("ar,au,at,be,br,bg,ca,cn,co,cz,eg,fr,de,gr,hk,hu,in,id,ie,il,it,jp,lv,lt,my,mx,ma,nl,nz,ng,no,ph,pl,pt,ro,sa,rs,sg,sk,si,za,kr,se,ch,tw,th,tr,ae,ua,gb,us,ve", 'World'),
        ('ar', 'Argentina'),
        ('au', 'Australia'),
        ('at', 'Austria'),
        ('be', 'Belgium'),
        ('br', 'Brazil'),
        ('bg', 'Bulgaria'),
        ('ca', 'Canada'),
        ('cn', 'China'),
        ('co', 'Columbia'),
        ('cz', 'Czech Republic'),
        ('eg', 'Egypt'),
        ('fr', 'France'),
        ('de', 'Germany'),
        ('gr', 'Greece'),
        ('hk', 'Hong Kong'),
        ('hu', 'Hungary'),
        ('in', 'India'),
        ('id','Indonesia'),
        ('ie', 'Ireland'),
        ('il', 'Israel'),
        ('it', 'Italy'),
        ('jp', 'Japan'),
        ('lv', 'Lativia'),
        ('lt', 'Lithuania'),
        ('my', 'Malaysia'),
        ('mx', 'Mexico'),
        ('ma', 'Morocco'),
        ('nl', 'Netherlands'),
        ('nz', 'New Zealand'),
        ('ng', 'Nigeria'),
        ('no', 'Norway'),
        ('ph', 'Philippines'),
        ('pl', 'Poland'),
        ('pt', 'Portugal'),
        ('ro', 'Romania'),
        ('sa', 'Saudi Arabia'),
        ('rs', 'Serbia'),
        ('sg', 'Singapore'),
        ('sk', 'Slovakia'),
        ('si', 'Slovenia'),
        ('za', 'South Africa'),
        ('kr', 'South Korea'),
        ('se', 'Sweden'),
        ('ch', 'Switzerland'),
        ('tw', 'Taiwan'),
        ('th', 'Thailand'),
        ('tr', 'Turkey'),
        ('ae', 'UAE'),
        ('ua', 'Ukraine'),
        ('gb', 'United Kingdom'),
        ('us', 'United States'),
        ('ve', 'Venuzuela')
    ]
    country = forms.ChoiceField(choices=choose_country,label="Select a Country",required=False)

class SortForm(forms.Form):
    Choice_Sort = [
        ('published_desc', 'Published Date Decending'),
        ('published_asc', 'Published Date Ascending'),
        ('popularity', 'Popularity'),
    ]
    sort = forms.ChoiceField(choices=Choice_Sort,label="Choose Sorting Method(default is Published Date Decending)", initial=['published_desc'], required=False)

class LanguageForm(forms.Form):
    Choice_Language = [
        ('ar', 'Arabic'),
        ('de', 'German'),
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('he', 'Hebrew'),
        ('it', 'Italian'),
        ('nl', 'Dutch'),
        ('no', 'Norwegian'),
        ('pt', 'Portuguese'),
        ('ru', 'Russian'),
        ('se', 'Swedish'),
        ('zh', 'Chinese')
    ]
    language = forms.ChoiceField(choices=Choice_Language,label="Choose Language", initial="en", required=False)


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True,widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Enter Email'}))
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Enter Password'}))
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm Password'}))
    captcha = ReCaptchaField()

    class Meta:
        model = User
        fields = ('username','email','password1','password2','captcha')

        widgets = {
            'username': forms.TextInput(attrs={
                'class':'form-control',
                'placeholder':'Enter Username'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username', max_length=254,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter Username'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Enter Password'}))
    captcha = ReCaptchaField()

class QueryForm(forms.Form):
    name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder':'Full Name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'E-mail'
    }))
    subject = forms.CharField(max_length=200,widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder':'Write the Subject of Your Query'
    }))
    query = forms.CharField(widget=forms.Textarea(attrs={
        'class':'form-control',
        'placeholder': 'write your query',
        'row':5,
        'column': 20
    }))
    captcha = ReCaptchaField()