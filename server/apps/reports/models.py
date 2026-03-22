from django.db import models

class Report(models.Model):
    report_id = models.AutoField(primary_key=True)
    neighbourhood = models.ForeignKey("habitability.Neighborhood", on_delete=models.CASCADE, related_name="reports")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="reports")
    title = models.TextField()
    description = models.TextField()
    severity = models.CharField(max_length=20)
    type = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    date_submitted = models.DateField()
    vote_count = models.IntegerField()

    # For our use/ testing
    def __str__(self):
        return self.title

class Votes(models.Model):
    vote_id = models.AutoField(primary_key=True)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="votes")
    report = models.ForeignKey("reports.Report", on_delete=models.CASCADE, related_name="votes")
    date_voted = models.DateField()

    # So one user can only vote on one report once
    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "report"], name="one_vote_per_user")]
    
    # For our use/ testing
    def __str__(self):
        return f"Vote {self.vote_id}"

class Comments(models.Model):
    comment_id = models.AutoField(primary_key=True)
    report = models.ForeignKey("reports.Report", on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="comments")
    reply_to = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # ADD THIS LINE

    def __str__(self):
        return f"Comment{self.comment_id}"
        

