name: Code of Conduct Violation Report
description: Report a Code of Conduct violation (This will be private)
title: "[CoC]: "
labels: ["code-of-conduct"]
assignees: ["project-maintainers"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to report a Code of Conduct violation. This form will be visible only to project maintainers.
  
  - type: input
    id: contact
    attributes:
      label: Contact Details
      description: How can we get in touch with you if we need more info?
      placeholder: ex. email@example.com
    validations:
      required: false

  - type: textarea
    id: description
    attributes:
      label: What happened?
      description: Please describe the incident
      placeholder: Please be as specific as possible
    validations:
      required: true

  - type: textarea
    id: evidence
    attributes:
      label: Evidence
      description: If possible, please provide links or screenshots (these will be kept private)
    validations:
      required: false

  - type: checkboxes
    id: confidentiality
    attributes:
      label: Confidentiality
      options:
        - label: I understand this report will be handled confidentially
          required: true 