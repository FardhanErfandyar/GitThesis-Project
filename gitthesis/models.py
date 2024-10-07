from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Project(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    collaborators = models.ManyToManyField(
        User,
        through="Collaborator",
        related_name="projects",
    )

    def __str__(self):
        return f"{self.name} (Updated: {self.updated_at})"


class Section(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="sections"
    )
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)  # Tambahkan updated_at di sini

    def save_new_version(self):
        """
        Save changes as a new version in the SectionVersion model.
        """
        new_version = SectionVersion.objects.create(
            section=self,
            content=self.content,
        )
        return new_version

    def get_history(self):
        """
        Retrieve the entire history of changes for this section.
        """
        return SectionVersion.objects.filter(section=self).order_by("-created_at")

    def apply_version(self, version_id):
        """
        Apply a previous version to the current section and save it as a new version.
        """
        try:
            old_version = SectionVersion.objects.get(id=version_id, section=self)
            # Apply the old version's content
            self.content = old_version.content
            # Save this as a new version
            self.save_new_version()
            # Save section with updated content
            self.save()

            # Update the project updated_at timestamp
            self.project.updated_at = timezone.now()
            self.project.save()

            return True
        except SectionVersion.DoesNotExist:
            return False

    def __str__(self):
        return f"Section of {self.project.name} (Created: {self.created_at})"


class SectionVersion(models.Model):
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="versions"
    )
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Version of Section {self.section.id} (Created: {self.created_at})"


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="project_images/")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Image for {self.project.name} (Uploaded: {self.created_at})"


class Collaborator(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    invited_at = models.DateTimeField(default=timezone.now)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} on {self.project.name} (Accepted: {self.is_accepted})"


class Comment(models.Model):
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user.username} on Section {self.section.id} (Created: {self.created_at})"
