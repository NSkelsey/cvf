from django.contrib.auth.models import User

def make_user():
    me = User.objects.create_user("admin", "d@d.com", "pass")
    me.save()


if __name__ == "__main__":
    make_user()


