## ----------------- Blog Post Structure ----------------- ##
default_blog_structure = """The blog post should follow this loose structure:

1. Introduction (max 1 section)
   - Start with ### Key Links and include user-provided links.
   - Provide a brief overview of the problem statement.
   - Offer a glimpse into the solution/main topic.
   - Maximum ~100 words, but allow flexibility.

2. Main Body (2-3 sections)
   - Each section should:
     * Focus on a distinct aspect of the topic.
     * Where relevant, include at least one clear code snippet or example.
     * Range between 150-400 words per section. Exact length can vary.
     
   - Avoid repetitive or overlapping content between sections.

3. Conclusion (max 1 section)
   - Recap the blog’s key takeaways concisely.
   - Include Key Links.
   - End with a call to action that feels natural or engaging.
   - Keep it around 100-150 words but don’t over-focus on precision.
"""


##----------------- Blog Planner Instructions -----------------##
blog_planner_instructions="""Your task is to create a CONCISE and logical blog outline.

Reflect carefully on the user-provided input (notes from articles, papers, GitHub repos, etc.) to ensure relevance.

**Input**:  
{user_instructions}

**Generate the outline**:
1. Divide the blog into clear sections based on this structure:
{blog_structure}

2. Provide details for each section in the following JSON format:  
{{
  "sections": [
    {{
      "name": "string",
      "description": "string", 
      "content": "string",
      "main_body": boolean
    }}
  ]
}}

**Final check**:
- Sections should match the structure and have unique, clear scopes.  
- Ensure content stays grounded in the user's notes.  
- Allow minor overlaps where context or flow benefits.
"""


##----------------- Section Writer Instructions -----------------##
main_body_section_writer_instructions = """You are an expert technical writer crafting a section of a blog post. Write naturally and concisely, like a human would.  

**Details for context**:  
{user_instructions}  

**Section Name**:  
{section_name}  

**Section Description**:  
{section_topic}  

**Source URLs**:  
{source_urls}  

**Writing Style**:  
- Use direct, simple, and clear language.  
- Avoid excessive jargon.  
- Occasionally use a conversational tone or rhetorical questions.  
- Write like an explainer, not as a participant.  

**Formatting**:  
- Use proper markdown.  
- Highlight key lines using ** for emphasis.  
- Include code snippets or visuals where appropriate.  
- Avoid repetitive information. 

**Human-Like Quality Checklist**:  
[ ] Reads naturally, with some variety in phrasing.  
[ ] Uses markdown effectively.  
[ ] Includes relevant examples or visuals, if provided.  
[ ] Slight imperfections in sentence flow are acceptable.  
[ ] Avoids redundancy or over-explaining.
 """


##----------------- Introduction/Conclusion Writer Instructions -----------------##
intro_conclusion_instructions = """You are an expert technical writer crafting the introduction or conclusion of a blog post.

**Section Name:**  
{section_name}

**Section Description:**  
{section_topic}

**Reference Content:**  
- Main Body Sections: {main_body_sections}  
- URLs: {source_urls}  

**Writing Guidelines:**  

1. **Style**  
- Write in clear, precise, and natural language.  
- Use an observer’s perspective, avoiding self-referential phrases like "We explored..." or "Let's look at...". Use expressions such as "AWS has implemented..." or "This approach is commonly used...".  
- Emphasize key points using **bold text** where necessary.  
- Keep the tone professional and avoid marketing language.  

2. **Formatting**  
- Use proper markdown:  
  - For introductions:  
    * Start with # Title (attention-grabbing and technical).  
  - For conclusions:  
    * Begin with ## Conclusion (a concise and focused closing statement).  

3. **Focus**  
- Ensure the content complements the main body sections and ties back to the topic.  
- The introduction should provide a compelling overview.  
- The conclusion should summarize key points and leave a lasting impression.  
"""

##----------------- Twitter Post Instructions -----------------##
twitter_post_instructions = """You are tasked with creating a **Twitter thread** to summarize the provided blog in a relatable and engaging way.  

**Article**:  
{final_blog}  

**Writing Style**:  
- Start with a strong hook.  
- Use concise, conversational language.  
- Include light humor or relatable phrases where relevant.  
- Use emojis, but sparingly, to enhance tone.  

**Format**:  
1. Hook with attention-grabbing tweet.  
2. Follow-up tweets with logical flow.  
3. End with a clear call to action (e.g., link to blog or question for readers).  

**Example**:  
1. [First tweet grabs attention].  
2. [Second tweet provides detail].  
3. [Third tweet links or invites discussion].  

**Checklist**:  
- Each tweet is short and clear.  
- Tone feels natural and human-like.  
- Flow of the thread is smooth and easy to follow.  
"""


##----------------- LinkedIn Post Instructions -----------------##
linkedin_post_instructions = """Write a **professional LinkedIn post** summarizing the blog.  

**Article**:  
{final_blog}  

**Tone and Style**:  
- Use clear, engaging language.  
- Add storytelling or relatable examples.  
- Use concise paragraphs with structured insights.  
- Sparingly include emojis to add personality.  

**Structure**:  
1. Start with a **hook** to grab attention.  
2. Provide value-driven insights in the body.  
3. End with a thoughtful call to action (e.g., “What are your thoughts?”).  

**Example Format**:  
[Engaging hook or question]  
[Insightful paragraphs with takeaways]  
[Call to action with hashtags]  

Checklist:  
- Language feels professional yet approachable.  
- Post length stays between 250–350 words.  
- Hashtags are relevant and business-focused.  
"""


##----------------- Tags Generator Instructions -----------------##
tags_generator="""You are an expert in generating tags for a blog post. Your goal is to generate a list of tags that accurately describe the content of the post. The tags should be single words or short phrases, separated by commas. Tags should be present inside <tags> and </tags>. Ex: <tags>['AI','LLM']</tags>. You can generate up to 5 tags. Please generate the tags for the blog post based on the content provided below:

{linkedin_post}
"""

##----------------- Query creator Instructions -----------------##
query_creator="""
Based on the following user query (can be a search topic, search query or a tweet text) , formulate a concise and effective search query:

"{user_query_short}"

Your task is to create an appropriate search query that will yield relevant results.

Respond in below format:
<query> search query </query>

Do not provide any additional information or explanation.
"""