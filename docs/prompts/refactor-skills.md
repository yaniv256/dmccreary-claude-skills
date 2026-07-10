# Refactor Skill Plan

Given to Claude Fable 5 in Planning Mode with Effort level set to "Extra"

!!! prompt
    Over the past 9 months I have developed a series of 30+ AI agent skills for generating high-quality interactive intelligent textbooks.  These skill have often been experiments and some skills are not organized coherently.  The skills have two rough divisions: the first set of skills generates the mkdocs framework for textbooks and the second set of skill builds interactive components such as MicroSims and interactive infographics.  Please review all the agent skill in the @skills directory and suggest any refactors that would make the skills better organized.  Pay careful attention to the fact that the title and descriptions of the skills need to fit in a 1% token budget and some models only have 200K tokens in their context window.  Suggest skills that can be combined and use the 
    /book-installer skill as an example of many functions in a single skill.