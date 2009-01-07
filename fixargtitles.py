from tcd.items.models import Argument
# one-off script to change the title of all arguments to the
# first 20 characters of the first comment by the plaintiff

def main():
    args = Argument.objects.order_by('start_date')
    for arg in args:
        arg.title= ''.join([arg.comment_set.order_by('pub_date')[1].comment[:20].replace('\r', ' '), '...'])
        arg.save()

if __name__ == "__main__":
    main()
