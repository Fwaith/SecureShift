from django.db import models



'''
class Comments(models.Model):
    comment_id = models.AutoField(primary_key=True)
    report = models.ForeignKey("reports.Report", on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="comments")
    reply_to = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    description = models.TextField()

    # For our use/ testing
    def __str__(self):
        return f"Comment{self.comment_id}"
        '''
