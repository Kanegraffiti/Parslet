# Come Build With Us!

Thank you for being here! We're thrilled you're thinking about contributing to Parslet. Whether you've found a typo, have an idea for a new feature, or want to fix a bug, your help means the world to us. We're excited to build this with you.

## Our Style: Keeping Things Tidy and Friendly

So that everyone can understand the code, we follow a few simple guidelines. Don't worry, it's not strict, and we have tools to make it super easy!

-   **Code Formatting:** We use a tool called `black` to make sure all our code looks the same.
-   **Code Quality:** We use `flake8` to automatically catch common mistakes.
-   **Commit Messages:** Think of these like a short, friendly note to your future self and to us. A simple message like `docs: explain battery mode better` is perfect.

You don't need to be an expert. The tools do most of the work for you!

## Getting Your Hands Dirty: The Fun Part!

Ready to jump in and write some code? Here’s how to get everything set up.

### Step 1: Install Everything You Need

This one command installs Parslet itself, plus all the tools we use for development.

```bash
pip install -r requirements.txt
```

### Step 2: Set Up Your Friendly Robot Co-Pilot

We use a cool tool called `pre-commit`. It's like a friendly robot that checks your code for any style issues *before* you share it. This way, you can be sure your code is perfect.

```bash
# First, install the tool itself
pip install pre-commit

# Now, set it up for this project
pre-commit install
```

That's it! Now, whenever you're about to save a change with `git commit`, your robot co-pilot will quickly format and check your code. If it finds anything, it will let you know.

## Ready to Share Your Awesome Work?

Once you've made your changes, here’s a quick checklist before you create a "Pull Request" (that's how you share your code with us).

1.  **Run the Checks:** Make sure your code is formatted nicely and passes all the checks. You can ask your robot co-pilot to check everything with this command:
    ```bash
    pre-commit run --all-files
    ```
2.  **Run the Tests:** This makes sure all the existing features still work perfectly after your changes.
    ```bash
    pytest
    ```
3.  **Keep it Clean:** Please try not to include large files that aren't code.
4.  **Explain Your Change:** Write a clear, simple description of what you changed and why. This helps us understand your brilliant idea!

And you're done! We can't wait to see what you've built. If you ever get stuck or have a question, please don't hesitate to open an issue. There are no silly questions here.
