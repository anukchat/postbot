# Agent Architecture

## Goal
Given a tweet and its metadata and reference documents for the tweet:
1. Identify type of tweet ['Technical','Research','NonTechnical','AI','NonAI']
2. Depending on the tweet and its metadata, generate tags to for the blog ['']
3. Trigger to ask user on creating blog post or not,
4. If answered yes, provide tweet type, tags, and a suggestion on style.
5. Ask for prompt template and style to be used [casual style, technical style, research style etc..], 
6. Once provided, trigger blog generation process (Create blog with reference images, reference repo, webpage, etc...,)
7. Once generated, show in a canvas style blog, where user can edit the blogs, save and download.
8. Optionally ask for user permission to approve for publishing.
9. Ask for publishing schedule, and add in a publishing calendar.
10. Complete the process and mark status as Scheduled. [Track status of the Post in a DB table ] (Investigation, BlogCreationDiscarded ,SystemBlogStarted, SystemBlogsGenerated, HumanBlogsEdited, HumanBlogsApproved, HumanBlogsScheduled, HumanBlogsPublished, BlogShareScheduled, BlogsSharePublished)


### Agents:
- TweetClassifier & TagGenerator
- PublishRecommender
- BlogGenerator based on styles
- Reviewer based on rules [preconfigured guidelines]
- HumanReviewer
- Scheduler [asks for permissions for scheduling]