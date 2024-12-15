# Documentation Style Guide

## Overview

This style guide provides standards for contributing to the Book Tracker documentation. Following these guidelines ensures consistency and clarity across all documentation.

## General Principles

1. **Clarity First**
   - Write for clarity and understanding
   - Use simple, direct language
   - Avoid jargon unless necessary
   - Define technical terms when first used

2. **User Focus**
   - Write from the user's perspective
   - Address the reader directly ("you")
   - Explain why, not just how
   - Include practical examples

3. **Consistency**
   - Use consistent terminology
   - Maintain consistent formatting
   - Follow established patterns
   - Use style guide conventions

## Markdown Guidelines

### Headers

```markdown
# Top-level Header (Document Title)
## Second-level Header (Major Sections)
### Third-level Header (Subsections)
#### Fourth-level Header (Details)
```

- Use Title Case for top-level headers
- Use Sentence case for all other headers
- No punctuation in headers
- Maximum of 4 header levels

### Lists

1. **Ordered Lists**
   ```markdown
   1. First item
   2. Second item
      - Sub-item
      - Sub-item
   3. Third item
   ```

2. **Unordered Lists**
   ```markdown
   - Main point
     - Supporting point
     - Supporting point
   - Main point
   ```

### Code Blocks

1. **Inline Code**
   ```markdown
   Use `backticks` for inline code, commands, or filenames
   ```

2. **Code Blocks**
   ````markdown
   ```python
   def example():
       return "Use language-specific code blocks"
   ```
   ````

### Links and References

1. **Internal Links**
   ```markdown
   [Link Text](relative/path/to/file.md#section)
   ```

2. **External Links**
   ```markdown
   [Link Text](https://example.com)
   ```

### Images

```markdown
![Alt Text](path/to/image.png "Optional Title")
```

- Include descriptive alt text
- Use relative paths
- Place images in `/docs/images/`
- Optimize images for web

## Writing Style

### Voice and Tone

1. **Active Voice**
   - ✅ "Click the button"
   - ❌ "The button should be clicked"

2. **Direct Address**
   - ✅ "You can configure..."
   - ❌ "Users can configure..."

3. **Present Tense**
   - ✅ "The command starts the server"
   - ❌ "The command will start the server"

### Formatting Conventions

1. **UI Elements**
   - Use bold for UI elements: **Save**, **Cancel**
   - Use quotes for field names: "Username"
   - Use code style for input: `example@email.com`

2. **File Paths**
   - Use code style: `config/settings.py`
   - Use forward slashes: `/path/to/file`
   - Include leading slash when absolute

3. **Commands**
   - Use code blocks for multi-line commands
   - Use inline code for single commands
   - Include output when relevant

### Documentation Types

1. **Tutorials**
   - Step-by-step instructions
   - Clear prerequisites
   - Expected outcomes
   - Complete examples

2. **How-to Guides**
   - Task-focused
   - Problem-solving approach
   - Practical examples
   - Common use cases

3. **Reference**
   - Accurate and complete
   - Structured consistently
   - Technical details
   - Cross-references

4. **Explanations**
   - Background information
   - Concepts and theory
   - Design decisions
   - Trade-offs

## Best Practices

### Structure

1. **Document Organization**
   - Clear hierarchy
   - Logical progression
   - Consistent sections
   - Related content grouped

2. **Section Length**
   - Keep sections focused
   - Use subheadings
   - Break up long content
   - Maintain readability

### Content

1. **Examples**
   - Provide realistic examples
   - Include context
   - Show expected output
   - Explain significance

2. **Procedures**
   - Clear prerequisites
   - Numbered steps
   - Verification steps
   - Troubleshooting tips

### Maintenance

1. **Version Control**
   - Update CHANGELOG.md
   - Follow versioning rules
   - Document changes
   - Review regularly

2. **Quality Control**
   - Check links
   - Verify examples
   - Test procedures
   - Update screenshots

## Review Process

1. **Self Review**
   - Check spelling/grammar
   - Verify formatting
   - Test all examples
   - Check all links

2. **Peer Review**
   - Technical accuracy
   - Style compliance
   - User perspective
   - Completeness

## Common Issues

### Avoid

1. **Language**
   - Passive voice
   - Complex jargon
   - Ambiguous pronouns
   - Colloquialisms

2. **Structure**
   - Deep nesting
   - Redundant information
   - Inconsistent formatting
   - Missing context

### Include

1. **Clarity**
   - Clear prerequisites
   - Expected outcomes
   - Error handling
   - Success criteria

2. **Context**
   - Use cases
   - Limitations
   - Alternatives
   - Related information

## Tools and Resources

1. **Recommended Tools**
   - Markdown editors
   - Spell checkers
   - Link validators
   - Image optimizers

2. **Style References**
   - Google Developer Documentation Style Guide
   - Microsoft Writing Style Guide
   - Chicago Manual of Style
   - Strunk & White's Elements of Style

## Questions and Support

Need help with documentation?
- Review existing documentation
- Check the style guide examples
- Ask in the #documentation channel
- Contact the documentation team 