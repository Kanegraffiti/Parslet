# Parslet Recipes: Real-World Examples

The best way to learn is by doing! We've cooked up a bunch of simple "recipes" (what we call workflows or case studies) to show you what Parslet can do in the real world.

You can find all of these in the `examples/` folder.

### 1. The "Hello World" Recipe
**File:** `examples/hello.py`

This is the perfect place to start. It's a super simple recipe that does some basic math. It's great for learning how to:
- Create a task.
- Connect tasks to each other.
- Run a recipe from the command line.

**Try it:**
```bash
parslet run examples/hello.py
```

### 2. The Photo Filter Recipe
**File:** `examples/image_filter.py`

This recipe shows you how to use Parslet to edit a photo. It's a mini-pipeline that will:
1. Load a picture.
2. Make it black and white.
3. Add a blur effect.
4. Save the new picture.

Because each step is a separate task, Parslet can run some of them at the same time to be more efficient!

**Try it (and see a picture of your recipe!):**
```bash
parslet run examples/image_filter.py --export-png pipeline.png
```
This will create a cool diagram of your workflow called `pipeline.png`.

### 3. The Text Cleaner-Upper Recipe
**File:** `examples/text_cleaner.py`

This is a great example of a data-cleaning recipe that you can run completely offline. It takes a messy text file and:
1. Makes everything lowercase.
2. Removes all the punctuation.
3. Counts how many times each word appears.
4. Saves the result as a clean JSON file.

**Try it:**
```bash
parslet run examples/text_cleaner.py
```

### 4. The Mini-Hospital AI Recipe
**File:** `examples/rad_pipeline.py`

This recipe shows off our **RAD by Parslet** idea. It's a mini-pipeline for a doctor in a remote clinic. It runs two small AI models on a medical image and saves the diagnosis.

**Try it:**
```bash
parslet run examples/rad_pipeline.py
```

### 5. The Video Frame Grabber
**File:** `examples/video_frames.py`

This recipe uses a popular tool called OpenCV to pull out all the individual frames (pictures) from a video file and count them.

**Try it:**
```bash
parslet run examples/video_frames.py --video my_video.mp4
```
(You'll need to have a video file named `my_video.mp4` for this to work).

---

We have many more examples for you to explore, from cleaning CSV files to simulating sensor data on a tiny computer. The best way to learn is to open up the files, read the simple Python code, and see how the `ParsletFuture` "IOUs" are passed from one task to the next.

### Want to Run Them All at Once?

We made a special script that runs all the main examples for you and prints out their results and how long they took to run.

```bash
python run_all_examples.py
```

Don't worry if you don't have all the extra libraries installed. The script is smart enough to skip any examples you don't have the tools for.