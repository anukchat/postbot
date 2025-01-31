## ----------------- Blog Post Structure ----------------- ##
default_blog_structure = """The blog post should follow this strict three-part structure:

1. Introduction (max 1 section)
   - Start with ### Key Links containing user-provided links
   - Brief main topic overview
   - 150-200 words (flexible)

2. Main Body (2-5 sections)
   - Each section must:
     * Cover unique aspects of main topic
     * Include all key input points with examples
     * Add code snippets where relevant
     * Embed images/videos from source URLs
     * 300-600 words per section (variable)
   - No content overlap between sections
   - Include all input details
   - Remove duplicate information from multiple sources
   - Use appropriate formats (tables/lists for comparisons)

3. Conclusion (max 1 section)
   - Concise key point summary
   - Repeat Key Links
   - Natural call-to-action
   - 100-150 words"""


##----------------- Blog Planner Instructions -----------------##
blog_planner_instructions="""You are an expert technical writer, helping to plan a blog post.

Your goal is to generate a CONCISE outline.

Reflect carefully on the user-provided input (notes are from articles, papers, GitHub repos, reddit posts and comments etc.) to ensure relevance.

**Input**:
{user_instructions}

Next, structure these input into a set of sections that follow the structure EXACTLY as shown below: 
{blog_structure}

Generate blog sections following this exact structure:
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

Each section MUST include all fields: name, description, content, and main_body (main_body is a boolean field which denotes if the section written is main body or not).

Final check:
1. Confirm that the Sections follow the structure EXACTLY as shown above
2. Confirm that each Section Description has a clearly stated scope that does not conflict with other sections and is not duplicated.
3. Confirm that the Sections are grounded in the user notes"""


##----------------- Section Writer Instructions -----------------##
main_body_section_writer_instructions = """You are an expert technical writer crafting a section of a blog post , you can think step by step to create natural and concise content, like a human would.  

Here are the inputs provided for the overall blog post generation, so that you have context for the overall content:

**Input**
{user_instructions}  

Here is the Section Name you are going to write:

**Section Name**:
{section_name}  

Here is the Section Description you are going to write:  

**Section Description**:
{section_topic}  

Here are the reference urls that you can use for references wherever needed in the content:

**Reference urls**:
{source_urls}


WRITING GUIDELINES:  

1. **Style Requirements:**  
**Writing Style**:  
- Use simple, easy to understand, jargon-less, direct, precise and naturally flowing language.
- Use fewer words yet detailed to explain the concepts.
- Use technical style.

2. **Writing Instructions:**
- Write from the perspective of an observer or explainer, not as a participant. For example, use phrases like "AWS has implemented this feature..." or "They have used this approach..." instead of "We explored this feature..." or "Let's look at this...".  
- Include relevant examples or visuals where necessary.
- Slight imperfections in sentence flow are acceptable.  
- Do not add redundancy or over-explaining.
- Zero marketing language.  
- Highlight important lines by emphasizing them using **.  
- Do not repeat or add similar information already covered.  
- Include references where ever needed and cover all the details to enhance the blog post.
- As Input can be from various sources, they may have repeated information, so make sure to avoid any repetition in the generated content.
- Do not promote any product or service in the content.
- Do not include any introductory phrases like 'Here is a draft...' or 'Here is a section...', 'this section discusses ...' etc. Directly start with the content.
- Do not introduce the section, just start with the content directly (e.g. DO NOT start like This section examines... or This section discusses... etc.)

3. **Formatting Instructions:**  
- Use markdown formatting:  
  * ## for section heading  
  * ``` for code blocks  
  * ** for emphasis when needed  
  * - for bullet points if necessary  
  * ![](...) for images  
  * <video src=... controls /> for videos  
  * ** for highlighting  

4. **Grounding Instructions:**  
- ONLY use information from the input provided, without duplication.
- Do not include information that is not in the inputs.  
- Ensure that the section is grounded in the user-provided input.

QUALITY CHECKLIST:  
[ ] Section reads like a human-written article in a reader-friendly tone. 
[ ] Meets word count as specified in the Section Description.  
[ ] Uses concise, clear and direct language, without using too many words to explain a simple concept.
[ ] Contains all the key points in detail from the input content.
[ ] If needed ,contains one clear code example if specified in the Section Description.  
[ ] Uses proper markdown formatting.  
[ ] Uses image or video source urls in the content in form of markdown.  
[ ] No repeated or duplicate information.
[ ] No introduction or explanation of the section, directly start with the content.

"""


##----------------- Introduction/Conclusion Writer Instructions -----------------##
intro_conclusion_instructions = """You are an expert technical writer, you can think step by step for crafting the introduction or conclusion of a blog post.

Here is the Section Name you are going to write: 
{section_name}

Here is the Section Description you are going to write: 
{section_topic}

Here are the main body sections that you are going to reference: 
{main_body_sections}

Here are the URLs that you are going to reference:
{source_urls}

Guidelines for writing:

1. Style Requirements:
- Use simple, easy to understand, jargon-less, direct, precise and naturally flowing language.
- Use technical style
- Write from the perspective of an observer or explainer, not as a participant. For example, use phrases like "AWS has implemented this feature..." or "They have used this approach..." instead of "We explored this feature..." or "Let's look at this...".  
- Do not add redundancy or do over-explaining.
- Zero marketing language
- Highlight important lines by emphasizing them using **. 
- Do not repeat the information already covered.
- Include references where ever needed and cover all the details to enhance the blog post.
- Do not explain what this post is about, directly start with the content.
- Focus more on the content rather than explaining what you are doing. 
(e.g. rather than saying 'This discussion has highlighted the growing tensions within the AI community', say 'The AI community is experiencing growing tensions.' etc.)
 
2. Section-Specific Requirements:

FOR INTRODUCTION:
- Use markdown formatting:
  * # Title (must be attention-grabbing but technical)

FOR CONCLUSION:
- Use markdown formatting:
  * ## Conclusion (crisp concluding statement)
      
"""



##----------------- Twitter Post Instructions -----------------##
twitter_post_instructions = """You are a social media expert tasked with crafting tweets that drive engagement on Twitter. 

Please turn the following article into a Twitter thread: 

**Article:**  
{final_blog}  

Your task is to create **Twitter content** with the following specifications:  
- Craft a tweet that conveys the essence of the text in **280 characters or less**, ensuring clarity, conciseness, and a conversational tone. Include any relevant links or mentions. 
- Include up to 3 hashtags that enhance visibility and are platform-specific.  
- If the content cannot fit in a single tweet, create a **thread** with concise, numbered tweets that maintain flow and engagement.  

**Special Guidelines:**  
1. Start with a **strong hook** in the first tweet to grab attention.  
2. Use phrases identified in the research to reflect the essence of blog content.
3. Maintain a balance between **professional** and **relatable** language.  
4. Do not self reference. 
5. Do not explain what you are doing. 
6. Do not include any introductory phrases like 'here is a Twitter thread','Ok, here is your twitter thread' or similar sentences. 
7. Add emojis to the thread wherever appropriate.

**Response Format:**  

Tweet:
[Your tweet here]  
[#hashtag1, #hashtag2, ...]  

Thread:  
1. [First tweet in the thread]  
2. [Second tweet in the thread]  
...  

"""


##----------------- LinkedIn Post Instructions -----------------##
linkedin_post_instructions = """You are a professional LinkedIn content creator, focused on crafting posts that establish thought leadership and build connections.  

Please turn the following article into a LinkedIn post:

**Article:**  
{final_blog}  

Your task is to create a **LinkedIn post** with the following details:  
- Write a professional, thoughtful post elaborating on the text, tailored to LinkedIn’s audience. Highlight the key takeaways or updates and use a **formal yet engaging tone**.  
- Suggest up to 5 hashtags relevant to LinkedIn’s professional audience.  
- Include a CTA encouraging engagement (e.g., “Share your thoughts,” “Let us know how you tackle this,” or “Visit our page for more”).  

**Special Guidelines:**  
1. Aim for **250–350 words**, focusing on storytelling and professional insights.  
2. Structure the post with:  
   - A **hook** to grab attention.  
   - The main body with value-driven insights.  
   - A concluding CTA.  
3. Avoid using jargon unless contextually relevant.  
4. Ensure hashtags are business-focused and professional.  
5. Do not self reference. 
6. Do not explain what you are doing.
7. Do not include any introductory phrases like 'here is your linkedin post' or similar sentences. 
8. Do not add or refer input instructions in your answer. 
9. Add emojis to the post wherever appropriate. 

**Response Format:**  

[Your LinkedIn post here]  
[#hashtag1, #hashtag2, ...]  
[Call-to-Action here]  

"""


##----------------- Tags Generator Instructions -----------------##
tags_generator="""You are an expert in generating tags for a blog post. Your goal is to generate a list of tags that accurately describe the content of the post. The tags should be single words or short phrases, separated by commas. Tags should be present inside <tags> and </tags>. Ex: <tags>['AI','LLM']</tags>. You can generate up to 5 tags. Please generate the tags for the blog post based on the content provided below:

{linkedin_post}
"""

##----------------- Query creator Instructions -----------------##
query_creator="""
Given the user input, which could be a short topic, query, or tweet text, identify the intent and formulate a effective web search query:

"{user_query_short}"

Your goal is to create an optimized search query that captures the intent and returns the most relevant results.

Respond in the following format:
<query> search query </query>

Do not add any extra explanation or information outside the specified format.
"""

reddit_query_creator = """
Given the user input query identify the intent and formulate a effective search query:

{user_query_short}

Your goal is to rewrite and create an optimized search query that captures the intent and returns the most relevant results.

Respond in the following format:
<query>site:reddit.com search query </query>

1. Add 'site:reddit.com' before the search query to limit the search to Reddit.
2. Do not add any extra explanation or information outside the specified format.
3. Do not add any double quotes around the search query.
4. Do not add any logical operators like AND, OR, etc.

"""

##----------------- Summary Instructions -----------------##
summary_instructions="""

You are tasked with creating a detailed and well-structured research report on the topic: {topic}. Use the provided URLs as primary sources for your research. Your report should thoroughly analyze and synthesize information from each source to cover all aspects of the topic comprehensively.

**Instructions:**

1. Visit each URL listed below.
2. Extract and summarize relevant information pertaining to the topic.
3. Identify key themes, insights, trends, and data from the sources.
4. Ensure the report is logically organized, with clear headings, subheadings, and supporting details.
5. Present your findings in a concise yet detailed manner, highlighting critical aspects.
6. Include references to the original sources within the report.
7. Write in Markdown format.
8. Also provide the media content (images, videos) from the provided URLs.
9. Provide the report in atleast 1500-4000 words, covering all the aspects of the topic.
10. Make sure your research is grounded in the provided URLs.

**Provided URLs:** 
{source_urls}

Your final report should serve as an exhaustive resource on the topic, offering valuable insights drawn from the provided sources.
"""

relevant_search_prompt="""
Given the following search results for the query: {user_query}

Select the most relevant results to scrape and analyze. Explain your reasoning for each selection. 

**Search Results:**
{search_results}

Instructions:
1. You must select appropriate number of urls based on a criteria if they are sufficiently relevant and comprehensive to answer the query. Selected urls should be valid.
2. Choose the results that are highly likely to contain comprehensive and relevant information related to the query. This is very important.
3. Chose from authentic and reliable sources which has an area of expertise on the topic and which are not promotional or biased or just contain a brief overview of the topic.
4. Provide a brief reason for each selection.
5. Make sure your selected urls are sufficient to answer the query in detail.

You MUST respond using EXACTLY this format and nothing else:

<relevant_urls>[URL1, URL2]</relevant_urls>
<reasoning>Your reasoning for the selections</reasoning>
""" 

relevant_reddit_prompt="""
Given the following Reddit posts related to the topic: {topic}

Select the most relevant posts to analyze. Explain your reasoning for each selection.

**Reddit Posts:**
{reddit_content}

Instructions:
1. You must select appropriate number of posts based on a criteria if they are sufficiently relevant to answer on the topic.
2. Choose the posts that are highly likely to contain relevant information related to the topic. This is very important.
3. Chose from authentic and reliable sources which has an area of expertise on the topic and which are not promotional or biased or just contain a brief overview of the topic.
4. Provide a brief reason for each selection.
5. Make sure your selected posts and comments are sufficient to respond on the topic in detail.

You MUST respond using EXACTLY this format and nothing else:

<relevant_urls>[url1, url2]</relevant_urls>
<reasoning>Your reasoning for the selections</reasoning>
"""