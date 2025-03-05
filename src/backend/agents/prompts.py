## ----------------- Blog Post Structure ----------------- ##
default_blog_structure = """The blog post should follow this structure, adapted for {content_type}:

1. Introduction (max 1 section)
   - Brief main topic overview tailored for {age_group}
   - Include primary keyword in first paragraph
   - 150-200 words (flexible)
   - Ensure no duplicate content is introduced and transitions are smooth
   - Adapt language complexity for {age_group}

2. Main Body (2-5 sections)
   - Each section must:
     * Cover unique aspects of main topic
     * Include all key input points with examples appropriate for {age_group}
     * Add code snippets where relevant (if technical content is appropriate for audience)
     * Embed images/videos from source URLs
     * Target 1-2 long-tail keywords in headers
     * 300-400 words per section (variable)
   - No content overlap between sections
   - Include all input details
   - Remove duplicate information from multiple sources
   - Use appropriate formats (tables/lists for comparisons)
   - Write in the voice of {persona}
   - Trim any leading/trailing whitespace

3. Conclusion (max 1 section)
   - Concise key point summary aligned with {content_type}
   - Add Key Links
   - Natural call-to-action appropriate for {age_group}
   - Reinforce primary keyword
   - 100-150 words
   - Ensure a clear wrap-up without repeating prior content"""


##----------------- Blog Planner Instructions -----------------##
blog_planner_instructions="""You are an expert {persona}, helping to plan a {content_type}.

Your goal is to generate a CONCISE outline tailored for {age_group}.

Reflect carefully on the user-provided input to ensure relevance and appropriate complexity level.

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

For each section, be sure to provide:
- Name - Clear and descriptive section name appropriate for {age_group}
- Description - An overview of specific topics to be covered each section, written in the voice of {persona}
- Content - Leave blank for now
- Main Body - Whether this is a main body section or an introduction / conclusion sections

Final check:
1. Confirm that the Sections follow the structure EXACTLY as shown above
2. Confirm that each Section Description has a clearly stated scope that does not conflict with other sections and is not duplicated.
3. Confirm that each Section Description includes:
   - Primary/secondary keyword targets
   - Semantic relationship to parent topic
4. Confirm sections include:
   - Header keyword optimization
   - Unique value propositions for search engines
5. Confirm that the Sections are grounded in the user notes
6. Confirm a final synthesis step that ensures logical flow, seamless transitions, and absence of duplicate text across sections.
7. Trim any unintended whitespace that might trigger unwanted markdown code formatting."""


##----------------- Section Writer Instructions -----------------##
main_body_section_writer_instructions = """You are an expert {persona} crafting a section of a {content_type}, you can think step by step to create natural and concise content for {age_group}.  

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
- Use language appropriate for {age_group}
- Maintain the voice of {persona}
- Follow the conventions of {content_type}
- Use simple, easy to understand, jargon-less, direct, precise and naturally flowing language.
- Use fewer words yet detailed to explain the concepts.
- Use technical style when appropriate for the audience.

2. **Writing Instructions:**
- Write from the perspective of an observer or explainer, not as a participant. For example, use phrases like "AWS has implemented this feature..." or "They have used this approach..." instead of "We explored this feature..." or "Let's look at this...".  
- Include relevant examples or visuals where necessary.
- Slight imperfections in sentence flow are acceptable.  
- Before finalizing, check for duplicate or repeated text and remove any redundancy.
- Do not add redundancy or over-explaining.
- Zero marketing language.  
- Highlight important lines by emphasizing them using **.  
- Do not repeat or add similar information already covered.  
- Include references where ever needed and cover all the details to enhance the blog post.
- As Input can be from various sources, they may have repeated information, so make sure to avoid any repetition in the generated content.
- Do not promote any product or service in the content.
- Trim any leading whitespace to avoid unintentional markdown code block formatting.
- If including a code snippet, ensure it is formatted with a markdown code block and the proper language specifier.
- Do not include direct sentences with words {persona}, {age_group}, {content_type} in the content.

3. **Formatting Instructions:**  
- Use markdown formatting 
- Use ** for highlighting and emphasizing important points.

4. **Grounding Instructions:**  
- ONLY use information from the input provided, without duplication.
- Do not include information that is not in the inputs.  
- Ensure that the section is grounded in the user-provided input.

5. **SEO Requirements:**
- Naturally integrate primary keywords (1-2% density)
- Use LSI keywords in explanations
- Include 1-2 internal links using anchor text, (When choosing internal links, consider linking to high-traffic or cornerstone content if available.)

QUALITY CHECKLIST:  
[ ] Section reads like a human-written article in a reader-friendly tone appropriate for {age_group}
[ ] Meets word count as specified in the Section Description  
[ ] Uses concise, clear and direct language, without using too many words to explain a simple concept
[ ] Contains all the key points in detail from the input content
[ ] If needed, contains one clear code example if specified in the Section Description  
[ ] Uses proper markdown formatting
[ ] Uses image or video source urls in the content in form of markdown  
[ ] No repeated or duplicate information
[ ] No introduction or explanation of the section, directly start with the content
[ ] Uses proper text formatting without duplication"""


##----------------- Introduction/Conclusion Writer Instructions -----------------##
intro_conclusion_instructions = """You are an expert {persona}, you can think step by step for crafting the section of {content_type}.

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
- Use language appropriate for {age_group}
- Write in the voice of {persona}
- Follow the conventions of {content_type}
- Use simple, easy to understand, jargon-less, direct, precise and naturally flowing language
- Use technical style when appropriate for the audience
- Write from the perspective of an observer or explainer, not as a participant. For example, use phrases like "AWS has implemented this feature..." or "They have used this approach..." instead of "We explored this feature..." or "Let's look at this...".  
- Do not add redundancy or do over-explaining
- Zero marketing language
- Highlight important lines by emphasizing them using ** 
- Do not repeat the information already covered
- Include references where ever needed and cover all the details to enhance the blog post
- Do not explain what this post is about, directly start with the content
- Focus more on the content rather than explaining what you are doing
(e.g. rather than saying 'This discussion has highlighted the growing tensions within the AI community', say 'The AI community is experiencing growing tensions.' etc.)
- If writing Introduction section, do not add Conclusion section and vice versa
- Trim any leading whitespace to prevent unintended markdown code block formatting
- Do not include direct sentences with words {persona}, {age_group}, {content_type} in the content (e.g. Do not add sentence like For investors aged 26-40 etc..)

 
2. **SEO Requirements:**
- If writing Introduction, it must contain:
  * Primary keyword in first 100 words
- If writing Conclusion, it should:
  * Include keyword variations
  * Use nofollow for external links

3. Section-Specific Requirements:

FOR INTRODUCTION (if writing introduction):
- Use # Title (must be attention-grabbing but technical)
- Always make sure that the Title starts with only one # and is followed by a space

FOR CONCLUSION (if writing Conclusion):
- Use ## Conclusion (crisp concluding statement)"""


##----------------- Twitter Post Instructions -----------------##
twitter_post_instructions = """You are a social media expert tasked with crafting tweets that drive engagement on Twitter. 

Please turn the following article into a Twitter thread: 

**Article:**  
{final_blog}  

Your task is to create **Twitter content** with the following specifications:  
- Craft a tweet that conveys the essence of the text in **280 characters or less**, ensuring clarity, conciseness, and a conversational tone. Include any relevant links or mentions. 
- Include up to 3 hashtags that enhance visibility and are platform-specific.  
- If the content cannot fit in a single tweet, create a **thread** with concise, numbered tweets that maintain flow and engagement.
- Include 1-2 branded hashtags with keywords
- Add UTM parameters to links

**Special Guidelines:**  
1. Start with a **strong hook** in the first tweet to grab attention.  
2. Use phrases identified in the research to reflect the essence of blog content.
3. Maintain a balance between **professional** and **relatable** language.  
4. Do not self reference. 
5. Do not explain what you are doing. 
6. Do not include any introductory phrases like 'here is a Twitter thread','Ok, here is your twitter thread' or similar sentences. 
7. Prior to composing, extract the key takeaways from the blog to inform the thread's content.
8. Trim any leading whitespace to avoid unintended code formatting.
9. Add emojis to the thread wherever appropriate.

**Response Format:**  

Tweet:
[Your tweet here]  
[#hashtag1, #hashtag2, ...]  

Thread:  
1. [First tweet in the thread]  
2. [Second tweet in the thread]  
...  """


##----------------- LinkedIn Post Instructions -----------------##
linkedin_post_instructions = """You are a professional LinkedIn content creator, focused on crafting posts that establish thought leadership and build connections.  

Please turn the following article into a LinkedIn post:

**Article:**  
{final_blog}  

Your task is to create a **LinkedIn post** with the following details:  
- Write a professional, thoughtful post elaborating on the text, tailored to LinkedIn's audience. Highlight the key takeaways or updates and use a **formal yet engaging tone**.  
- Suggest up to 5 hashtags relevant to LinkedIn's professional audience.  
- Include a CTA encouraging engagement (e.g., "Share your thoughts," "Let us know how you tackle this," or "Visit our page for more").
- Include 3-5 industry-specific hashtags
- Add rich media preview optimization
- Use LinkedIn Pulse keyword formatting
- Prior to writing, extract and summarize the key insights from the blog to shape the post's narrative.

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
9. Trim any leading whitespace to prevent unintentional code block formatting.
10. Add emojis to the post wherever appropriate. 

**Response Format:**  

[Your LinkedIn post here]  
[#hashtag1, #hashtag2, ...]  
[Call-to-Action here]"""


##----------------- Tags Generator Instructions -----------------##
tags_generator="""You are an expert in generating tags for a blog post. Your goal is to generate a list of tags that accurately describe the content of the post. The tags should be single words or short phrases, separated by commas. Tags should be present inside <tags> and </tags>. Ex: <tags>['AI','LLM']</tags>. You can generate up to 5 tags. Please generate the tags for the blog post based on the content provided below:

{linkedin_post}"""

##----------------- Query creator Instructions -----------------##
query_creator = """
Given a blog topic or theme, identify the intent and formulate an optimized web search query:

"{user_query_short}"

Formulate a search query that includes relevant keywords and entities to retrieve the most pertinent results.

Respond in the following format:
<query> search query </query>

Do not add any extra explanation or information outside the specified format."""


twitter_query_creator = """
Given a short tweet text, identify the intent and formulate an optimized web search query:

"{user_query_short}"

Interpret any informal language, hashtags, or emojis to extract the underlying intent. Formulate a search query that includes relevant keywords and entities to retrieve the most pertinent results.

Respond in the following format:
<query> search query </query>

Do not add any extra explanation or information outside the specified format.

Example:
Tweet:
"Introducing 1.58bit DeepSeek-R1 GGUFs! 🐋 DeepSeek-R1 can now run in 1.58-bit, while being fully functional. We shrank the 671B parameter model from 720GB to just 131GB - an 80% size reduction."

Expected Output:
<query> 1.58bit DeepSeek-R1 GGUF </query>"""


reddit_query_creator = """
Given the user input query identify the intent and formulate a effective search query:

{user_query_short}

Your goal is to rewrite and create an optimized search query that captures the intent and returns the most relevant results.

Respond in the following format:
<query>site:reddit.com search query </query>

1. Add 'site:reddit.com' before the search query to limit the search to Reddit.
2. Do not add any extra explanation or information outside the specified format.
3. Do not add any double quotes around the search query.
4. Do not add any logical operators like AND, OR, etc."""

##----------------- Summary Instructions (continued) -----------------##
summary_instructions="""
You are tasked with creating a detailed and well-structured research report on the topic: {topic}. Use the provided URLs as primary sources for your research. Your report should thoroughly analyze and synthesize information from each source to cover all aspects of the topic comprehensively.

**Instructions:**

1. Visit each URL listed below.
2. Extract and summarize relevant information pertaining to the topic.
3. Identify key themes, insights, trends, and data from the sources.
4. Ensure the report is logically organized, with clear headings, subheadings, and supporting details.
5. Present your findings in a concise yet detailed manner, highlighting critical aspects.
6. Include references to the original sources within.
7. Write in Markdown format.
8. Also provide the media content (images, videos) from the provided URLs.
9. Provide the report in atleast 1500-4000 words, covering all the aspects of the topic.
10. Make sure your research is grounded in the provided URLs.

**Provided URLs:** 
{source_urls}

Your final report should serve as an exhaustive resource on the topic, offering valuable insights drawn from the provided sources."""

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
<reasoning>Your reasoning for the selections</reasoning>"""

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
<reasoning>Your reasoning for the selections</reasoning>"""

## ----------------- Blog Reviewer Instructions ----------------- ##
blog_reviewer_instructions = """You are the final reviewer and editor responsible for validating and enhancing the overall quality of the generated {content_type} before final submission.

**Input**
{blog_input}

Your tasks:

1. **Template Compliance:**
   - Verify content is appropriate for {age_group}
   - Confirm the voice matches {persona}
   - Ensure format follows {content_type} conventions

2. **Structural Verification:**
   - Confirm the content strictly adheres to the blog post structure (Introduction, Main Body, Conclusion)
   - Ensure each section meets its specific guidelines (e.g., word count, keyword placement, internal linking, media inclusion)

3. **Content Integrity:**
   - Identify and remove any duplicate or repeated text across sections
   - Ensure smooth transitions and logical flow between sections
   - Verify that no unintended markdown code formatting occurs due to leading/trailing whitespace

4. **Formatting & SEO Checks:**
   - Validate that all code snippets are properly formatted with markdown code blocks and appropriate language specifiers
   - Check that internal links and other markdown elements (tables, lists, images, videos) are correctly formatted
   - Ensure primary and secondary keywords are naturally integrated per the dynamic SEO guidelines
   - Confirm that headings and subheadings follow the required format (e.g., # Title for Introduction, ## Conclusion for Conclusion)

5. **Editorial Quality:**
   - Ensure the language is clear, concise, and appropriate for the target audience
   - Remove any redundant or over-explained content
   - Confirm that the content is reader-friendly, coherent, and free of marketing language
   - Verify that technical concepts are explained at a level appropriate for {age_group}

Your output must follow this exact format:

<final_review>
[Your final reviewed content with any adjustments made]
</final_review>
<review_summary>
[Summary of adjustments and reasoning, if any]
</review_summary>

Do not add any additional commentary or explanations outside of the specified output format."""