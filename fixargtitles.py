from tcd.items.models import Argument

def main():
    args = Argument.objects.order_by('start_date')
    for arg in args:
        arg.title= ''.join([arg.comment_set.all()[1].comment[:20].replace('\r', ' '), '...'])
        arg.save()

if __name__ == "__main__":
    main()
