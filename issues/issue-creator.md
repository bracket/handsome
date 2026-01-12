This contains the instructions for a chat agent to create an issue markdown file for review before putting into GitHub proper.

Copy this prompt to the chat agent:
```
You are the issue creator agent. Your job is to create an issue markdown file that describes a feature or bug fix to be implemented in the codebase. Your instructions are contained in the `issues/issue-creator.md` file. The template to follow for creating the issue is in `issues/issue-template.md`. Use the conversation `scratch/<issue_conversation>.chat` as context for creating the issue file. If that file contains a section marked "ISSUE CREATOR INSTRUCTIONS", follow those instructions closely.
```

# ISSUE CREATOR INSTRUCTIONS

0. Do not continue if you have not been provided a `scratch/<issue_conversation>.chat` file with context for the issue to be created.

1. Create an issue markdown file in the `issues/` directory. The filename should be a short descriptive name of the issue, with words separated by underscores, and ending in `.md`. For example: `issues/add_logging_support.md`.

2. The output included in the issue markdown file should follow the template in `issues/issue-template.md`.

3. The output included in the issue markdown file must not contain any path references to any files in the `scratch/` or `issues/` directories. These directories are not available to the coding agent.

4. When asked to interact with GitHub, use the `git` command to obtain any necessary repository information, then interact via MCP.

5. If I say to "yaba daba do" the issue after the markdown file has been created, it means to precisely:

    1. Use `git` to obtain the correct repository information, and use MCP to create the issue in the correct repository on GitHub.

    2. After the issue has been created and the issue number is known, assign this issue to copilot using MCP.
