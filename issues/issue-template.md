### **Issue Title:**
[Concise, imperative description of the task]

---

## **Objective**
Describe the desired outcome in 1–2 sentences.

---

## **Background / Context**
Provide only the information required for the task:
- Relevant subsystem or module overview
- Links to internal docs or code comments
- Specific files or functions the agent must read before making changes

---

## **Inputs**
List all required inputs and their locations.

- Code to reference:
  - `path/to/fileA.ext`
  - `path/to/fileB.ext`
- External specification:
  - [link or embed]
- Required constants, schemas, or sample payloads

---

## **Requirements**
Define explicit expectations.

**Functional requirements:**
- [Requirement 1]
- [Requirement 2]

**Technical constraints:**
- [Constraint 1]
- [Constraint 2]

**Coding standards:**
- Follow patterns in: `path/to/example.ext`
- Maintain compatibility with: `[module names]`

**Forbidden modifications:**
- Do **not** modify:
  - `path/to/file`
  - `directory/to/avoid/`

---

## **Tasks for Copilot**
Provide a deterministic, ordered set of actions.

1. [Step 1]
2. [Step 2]
3. [Step 3]
4. [Additional steps as needed]

---

## **Acceptance Criteria**
The issue is complete when all of the following are met:

- [Criterion 1]
- [Criterion 2]
- [Criterion 3]
- [Criterion 4]

---

## **Verification Checklist (for the Agent)**
The agent must validate the following before closing the issue:

- [ ] All modified code compiles without errors
- [ ] All unit/integration tests pass
- [ ] All requirements are implemented as specified
- [ ] No forbidden files were modified
- [ ] All tasks in “Tasks for Copilot” are complete
- [ ] All acceptance criteria are satisfied
