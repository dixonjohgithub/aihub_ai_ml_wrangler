# Claude.md - Project Development Guide

## Standard Workflow

1. **Initial Analysis**: First think through the problem, read the codebase for relevant files, and write a plan to projectplan.md. Always read projectplan.md at the start of every new conversation.

2. **Task Planning**: The plan should have a list of todo items that you can check off as you complete them immediately.

3. **Plan Verification**: Before you begin working, check in with me and I will verify the plan.

4. **Execution**: Then, begin working on the todo items, marking them as complete as you go immediately upon completion.

5. **Communication**: Every step of the way just give me a high level explanation of what changes you made.

6. **Simplicity First**: Make every task and code change you do as simple as possible. We want to avoid making any massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity.

7. **Documentation**: Add a review section to the todo.md file with a summary of the changes you made and any other relevant information.

8. **Task Discovery**: Add newly discovered tasks to the projectplan.md file.

9. **Root Cause Analysis**: DO NOT BE LAZY. NEVER BE LAZY. IF THERE IS A BUG FIND THE ROOT CAUSE AND FIX IT. NO TEMPORARY FIXES. YOU ARE A SENIOR DEVELOPER. NEVER BE LAZY

10. **Minimal Impact**: MAKE ALL FIXES AND CODE CHANGES AS SIMPLE AS HUMANLY POSSIBLE. THEY SHOULD ONLY IMPACT NECESSARY CODE RELEVANT TO THE TASK AND NOTHING ELSE. IT SHOULD IMPACT AS LITTLE CODE AS POSSIBLE. YOUR GOAL IS TO NOT INTRODUCE ANY BUGS. IT'S ALL ABOUT SIMPLICITY

## Developer Best Practices

### Test-Driven Development (TDD) Workflow

1. **Write Tests First**: Before implementing any feature or fix, write unit tests that define the expected behavior
2. **Red-Green-Refactor Cycle**:
   - RED: Write a failing test for the new functionality
   - GREEN: Write minimal code to make the test pass
   - REFACTOR: Improve the code while keeping tests green
3. **Test Coverage**: Ensure each task and sub-task has corresponding unit tests
4. **Test Isolation**: Each test should be independent and not rely on other tests
5. **Test Naming**: Use descriptive test names that explain what is being tested and expected outcome

### Server Health Checks

1. **Frontend Server Verification**:
   ```bash
   curl -I http://localhost:[PORT] || echo "Frontend server is not running"
   ```

2. **Backend Server Verification**:
   ```bash
   curl -I http://localhost:[PORT]/health || echo "Backend server is not running"
   ```

3. **Always verify both servers are running before:
   - Starting development work
   - Running integration tests
   - Submitting pull requests

### File Documentation Standards

Every major file must include a header comment with:

```javascript
/**
 * File: [filename]
 * 
 * Overview:
 * [Brief description of what this file does]
 * 
 * Purpose:
 * [Why this file is needed for the project]
 * 
 * Dependencies:
 * - [List all external dependencies]
 * - [List all internal module dependencies]
 * 
 * Last Modified: [Date]
 * Author: [Name/Claude]
 */
```

### Version Control Best Practices

1. **Never Commit to Main**: The main branch should always be production-ready
2. **Branch Naming Convention**:
   - Feature branches: `feature/task-description`
   - Bug fixes: `fix/bug-description`
   - Hotfixes: `hotfix/critical-issue`
3. **Branch Workflow**:
   - Create a new branch for each task
   - Make atomic commits with clear messages
   - Push changes to the feature branch regularly
4. **Pull Request Process**:
   - Complete all tests and verify they pass
   - Ensure code follows project standards
   - Request user confirmation with "y" or "yes" before submitting PR
   - Include a summary of changes in the PR description
   - Reference any related issues or tasks

### Claude Code Specific Best Practices

1. **Project Structure Setup**:
   - Always create and maintain a `projectplan.md` file
   - Keep a running `todo.md` file with checkboxes for task tracking
   - Document all decisions and rationale in project files

2. **Code Analysis**:
   - Read and understand existing code before making changes
   - Use `tree` command to understand project structure
   - Identify all files that will be impacted by changes

3. **Implementation Guidelines**:
   - Make incremental changes that can be tested independently
   - Provide clear console output for each step
   - Use error handling and provide meaningful error messages
   - Always clean up resources (close files, connections, etc.)

4. **Testing Protocol**:
   - Run existing tests before making changes
   - Run tests after each significant change
   - Create test files with `.test.js` or `.spec.js` extensions
   - Include both positive and negative test cases

5. **Communication**:
   - Provide status updates after each completed sub-task
   - Clearly indicate when waiting for user input
   - Summarize changes made in each work session
   - Alert user to any potential issues or concerns

### Code Quality Checklist

Before considering any task complete:

- [ ] All tests pass
- [ ] Code follows project style guidelines
- [ ] No console errors or warnings
- [ ] File documentation headers are updated
- [ ] Dependencies are properly declared
- [ ] No hardcoded values (use environment variables)
- [ ] Error handling is comprehensive
- [ ] Code is DRY (Don't Repeat Yourself)
- [ ] Complex logic includes inline comments
- [ ] Performance considerations addressed
- [ ] Security best practices followed
- [ ] Accessibility requirements met (for frontend)

## Advanced Debugging with Claude Code

### Core Debugging Principles

1. **Avoid Debugging Loops**:
   - Set a maximum of 3 attempts for any single bug
   - If not resolved after 3 attempts, stop and reassess the entire approach
   - Document each attempt and what was learned
   - Never repeat the same fix attempt twice

2. **Systematic Debugging Workflow**:
   ```
   1. OBSERVE - Gather all error messages and symptoms
   2. HYPOTHESIZE - Form a specific theory about the cause
   3. TEST - Write console.log statements to verify theory
   4. ANALYZE - Review output and refine understanding
   5. FIX - Make minimal targeted change
   6. VERIFY - Confirm fix works and doesn't break other features
   ```

### Console Debugging Strategy

1. **Strategic Console.log Placement**:
   ```javascript
   // Debug entry points
   console.log('=== ENTERING FUNCTION: functionName ===');
   console.log('Input parameters:', { param1, param2 });
   
   // Debug critical decision points
   console.log('DECISION POINT: condition check');
   console.log('Condition value:', conditionVariable);
   
   // Debug data transformations
   console.log('BEFORE transformation:', data);
   // ... transformation code ...
   console.log('AFTER transformation:', data);
   
   // Debug exit points
   console.log('=== EXITING FUNCTION: functionName ===');
   console.log('Return value:', returnValue);
   ```

2. **Numbered Debug Statements**:
   ```javascript
   console.log('[DEBUG 1] Starting server initialization...');
   console.log('[DEBUG 2] Config loaded:', config);
   console.log('[DEBUG 3] Database connection attempt...');
   console.log('[DEBUG 4] Routes registered successfully');
   ```

3. **Error Boundary Logging**:
   ```javascript
   try {
     console.log('[ATTEMPT] Trying operation X...');
     // operation code
     console.log('[SUCCESS] Operation X completed');
   } catch (error) {
     console.error('[ERROR] Operation X failed:');
     console.error('Error Type:', error.name);
     console.error('Error Message:', error.message);
     console.error('Stack Trace:', error.stack);
   }
   ```

### Claude Code Specific Debugging Practices

1. **Debug Information Gathering**:
   - Always read the COMPLETE error message
   - Check file paths are correct (use `pwd` and `ls` to verify)
   - Verify environment variables are set
   - Confirm all dependencies are installed
   - Check server ports are not already in use

2. **Progressive Debugging Approach**:
   ```bash
   # Step 1: Verify file exists
   ls -la filename.js
   
   # Step 2: Check syntax
   node --check filename.js
   
   # Step 3: Run with verbose logging
   DEBUG=* node filename.js
   
   # Step 4: Isolate problem area
   # Comment out sections systematically
   ```

3. **Anti-Loop Patterns**:
   - **NEVER** make random changes hoping something works
   - **ALWAYS** have a hypothesis before making a change
   - **DOCUMENT** what each change attempt accomplished
   - **STOP** after 3 failed attempts and ask for user guidance

### Debugging Checklist

Before starting any debugging session:

- [ ] Read the ENTIRE error message carefully
- [ ] Note the exact line number and file where error occurs
- [ ] Check if error is consistent or intermittent
- [ ] Verify all servers are running (frontend/backend)
- [ ] Confirm latest code changes are saved
- [ ] Ensure dependencies match package.json

### Common Debugging Scenarios

1. **Module Not Found Errors**:
   ```javascript
   console.log('Current directory:', process.cwd());
   console.log('Module paths:', module.paths);
   console.log('Checking for file:', require.resolve('./module'));
   ```

2. **Undefined Variable Errors**:
   ```javascript
   console.log('Type of variable:', typeof variableName);
   console.log('Variable exists:', variableName !== undefined);
   console.log('Variable value:', variableName);
   console.log('Variable properties:', Object.keys(variableName || {}));
   ```

3. **Async/Promise Issues**:
   ```javascript
   console.log('[ASYNC-1] Starting async operation');
   const result = await asyncOperation()
     .then(res => {
       console.log('[ASYNC-2] Success:', res);
       return res;
     })
     .catch(err => {
       console.log('[ASYNC-3] Error:', err);
       throw err;
     });
   console.log('[ASYNC-4] Final result:', result);
   ```

4. **API/Network Debugging**:
   ```javascript
   console.log('REQUEST URL:', url);
   console.log('REQUEST METHOD:', method);
   console.log('REQUEST HEADERS:', headers);
   console.log('REQUEST BODY:', JSON.stringify(body, null, 2));
   // After response
   console.log('RESPONSE STATUS:', response.status);
   console.log('RESPONSE HEADERS:', response.headers);
   console.log('RESPONSE BODY:', responseBody);
   ```

### Breaking Out of Debug Loops

**Signs you're in a debugging loop:**
- Making the same change multiple times
- Error message hasn't changed after 2 attempts
- Trying variations without understanding why
- Feeling frustrated or confused

**How to break out:**

1. **STOP and Document**:
   ```markdown
   ## Debug Session [timestamp]
   
   ### Original Error:
   [paste complete error]
   
   ### Attempts Made:
   1. [What you tried] -> [Result]
   2. [What you tried] -> [Result]
   3. [What you tried] -> [Result]
   
   ### What We Know:
   - [Fact 1]
   - [Fact 2]
   
   ### What We Don't Know:
   - [Unknown 1]
   - [Unknown 2]
   
   ### Next Steps:
   - Ask user for guidance
   - Try completely different approach
   - Research documentation
   ```

2. **Reset to Known Good State**:
   ```bash
   git status  # Check what's changed
   git diff    # Review changes
   git stash   # Temporarily save changes
   # Test if original still works
   git stash pop  # Reapply changes one by one
   ```

3. **Simplify the Problem**:
   - Create minimal reproduction case
   - Remove all unnecessary code
   - Test with hardcoded values
   - Isolate the specific failing component

### Debug Output Standards

Always structure debug output for clarity:

```javascript
// Use separators for sections
console.log('=====================================');
console.log('   DEBUGGING: User Authentication    ');
console.log('=====================================');

// Use prefixes for different types
console.log('[INFO] Server starting on port 3000');
console.log('[WARN] Using default configuration');
console.log('[ERROR] Database connection failed');
console.log('[DEBUG] Raw query result:', data);
console.log('[SUCCESS] Operation completed');

// Use indentation for nested operations
console.log('Starting main process...');
console.log('  -> Loading configuration');
console.log('    -> Reading config file');
console.log('    -> Parsing JSON');
console.log('  -> Initializing database');
console.log('    -> Creating connection pool');
```

### Emergency Debugging Protocol

If stuck after 3 attempts:

1. **Full Status Report**:
   ```javascript
   console.log('=== EMERGENCY DEBUG REPORT ===');
   console.log('Node Version:', process.version);
   console.log('Current Directory:', process.cwd());
   console.log('Environment:', process.env.NODE_ENV);
   console.log('Memory Usage:', process.memoryUsage());
   console.log('Active Handles:', process._getActiveHandles().length);
   console.log('Active Requests:', process._getActiveRequests().length);
   ```

2. **Ask User for Help**:
   - Provide complete error message
   - Show last 3 console.log outputs
   - List what you've tried
   - Suggest alternative approaches
   - Request specific guidance

### Remember for Debugging

- **One change at a time**: Never make multiple changes simultaneously
- **Verify each fix**: Confirm each change has expected effect
- **Keep notes**: Document what works and what doesn't
- **Use version control**: Commit working states before debugging
- **Time box**: Set maximum time (15 min) per debugging session
- **Ask for help**: After 3 attempts, always ask for user guidance

## Project File Management

### Essential Project Files

1. **projectplan.md**: Master planning document with project goals and architecture
2. **todo.md**: Current task list with checkboxes
3. **Claude.md**: This file - development guidelines and standards
4. **README.md**: Project overview and setup instructions
5. **.gitignore**: Specify files to exclude from version control
6. **package.json**: Dependencies and scripts (for Node.js projects)
7. **tests/**: Directory containing all test files

### File Naming Conventions

- Use lowercase with hyphens for file names: `user-service.js`
- Test files: `[filename].test.js` or `[filename].spec.js`
- Component files (React): PascalCase `UserProfile.jsx`
- Utility files: `utils/[functionality].js`
- Configuration files: `config/[environment].config.js`

## Remember

- **Simplicity is key**: Every solution should be as simple as possible
- **Test everything**: No code without tests
- **Document clearly**: Future you (or another developer) will thank you
- **Communicate frequently**: Keep the user informed of progress
- **Never skip steps**: Follow the workflow systematically
- **Quality over speed**: Better to do it right than to do it twice