# Java Modernization

## Overview

This guide walks you through the process of modernizing Java applications using Bob.

## Reference Repository

For Java Modernization, you will fork and work with the VulnerableSampleApp application from:
```bash
https://github.com/Client-Engineering-Indonesia/VulnerableSampleApp
```

**Important:** Each participant will fork this repository to their own GitHub account to ensure everyone has their own copy to work with.

Later, after this lab is finished, you can find a reference example of the upgraded Java application here:
```bash
https://github.com/Client-Engineering-Indonesia/VulnerableSampleApp
```

## Prerequisites

> 👀 **Lab 1 ini adalah sesi demo** — presenter yang akan menjalankan langkah-langkahnya. Kamu cukup menyaksikan dan memahami prosesnya. **Tidak perlu install apapun untuk Lab 1.**

Untuk referensi (jika kamu ingin mencoba sendiri di lain waktu):

- **IBM Bob IDE** — Versi terbaru, sudah login
- **SDKMAN! + Maven** — Untuk build Java. Install via `curl -s "https://get.sdkman.io" | bash`, lalu `sdk install maven`
- **Java JDK 17+** — Target upgrade version

## Forking the Repository

Before you begin the Java modernization process, you need to create your own copy (fork) of the VulnerableSampleApp repository.

### What is a Fork?

A **fork** is your personal copy of a repository that lives in your GitHub account. When you fork a repository:
- You get a complete, independent copy with all its history
- You can make changes without affecting the original repository
- It's perfect for learning and experimentation
- Your fork maintains a connection to the original repository

### Step-by-Step Forking Instructions

#### Step 1: Navigate to the Repository

Open your web browser and go to:
```
https://github.com/Client-Engineering-Indonesia/VulnerableSampleApp
```

![Repository homepage](image/01-java-repo.png)

#### Step 2: Click the Fork Button

In the top-right corner of the repository page, click the **Fork** button.

![Fork button](image/02-java-fork-button.png)

#### Step 3: Configure Fork Settings and Create Fork

On the fork creation page, you'll see several options:

1. **Owner**: Select your GitHub account (should be pre-selected)
2. **Repository name**: Keep it as `VulnerableSampleApp` or customize if desired
3. **Description**: Optional - you can add a description
4. **Copy the main branch only**: ✅ **Keep this checked**
   - This ensures you only copy the main branch
   - Makes the fork faster and simpler
   - Provides a cleaner experience for this lab

Click the **Create fork** button at the bottom of the page.

![Create fork](image/03-create-fork.png)

#### Step 4: Wait for Fork Completion

GitHub will create your fork. This usually takes a few seconds. Once complete, you'll be redirected to your forked repository.

![Forked repository](image/04-forked-repo.png)

#### Step 5: Clone Your Fork Locally

Now that you have your own fork, clone it to your local machine **in the Lab1-java-modernization directory**:

1. On your forked repository page, click the **Code** button
2. Copy the repository URL (HTTPS or SSH)
3. Open your terminal and navigate to the Lab1 directory:

```bash
cd Lab1-java-modernization
git clone <your-forked-repository-url>
cd VulnerableSampleApp
```

![Clone fork](image/05-fork-clone.png)

**Example:**
```bash
cd Lab1-java-modernization
git clone https://github.com/Client-Engineering-Indonesia/VulnerableSampleApp.git
cd VulnerableSampleApp
```

**Note:** Cloning into the Lab1-java-modernization directory keeps your workspace organized and ensures all lab materials are in one place.

✅ **You now have your own copy of the VulnerableSampleApp ready for Java modernization!**

## Step-by-Step Java Modernization Guide

### Step 1: Open Your Forked Repository in Bob

After cloning your forked repository, open the `VulnerableSampleApp` folder in Bob:

1. Launch IBM Bob IDE
2. Click **File** → **Open Folder**
3. Navigate to your cloned `VulnerableSampleApp` directory
4. Click **Open**

Bob will detect the Java application and automatically enable the Java modernization mode.

![Open folder](image/06-open-folder.png)

### Step 2: Start Java Modernization

Bob will detect the Java application and automatically enable the Java modernization mode. Before starting, ensure that all prerequisites are met (SDKMAN and Maven installation).

**There are two ways to start the Java modernization process:**

**Option 1: Use the Workflow Button (Recommended for First-Time Users)**

If you see the **Java Modernization** workflow widget in Bob's chat interface, click the **Start** button. This provides a guided workflow experience.

![Java Modernization Workflow](image/07-java-modernisation_workflow.png)

**Option 2: Use the Command**

Alternatively, type `/start_java_modernization` in the chat interface. This command initializes Bob's Java modernization workflow and prepares the assistant to analyze your project.

![Start Java modernization](image/08-start-java-modernization.png)

> 💡 **Tip:** The workflow button provides a more visual, step-by-step experience, while the command gives you direct access to the modernization process. Both methods achieve the same result.

### Step 3: Provide Project Path

Provide the full path to your Java project directory. Bob will use this path to access and analyze your codebase.

![Java modernization widget](image/09-java-modernization-widget.png)

### Step 4: Requirements Analysis

Bob will check the prerequisites and automatically analyze your project to identify the current Java version, dependencies, and potential upgrade requirements.

If you encounter issues, make sure you have installed SDKMAN and Maven, restart Bob and try again.

![Analyze requirements](image/10-analyze-bob.png)

### Step 5: Select Java Update

From the available options, select the Java update feature.

![Select Java](image/11-select-java.png)

### Step 6: Choose Java Upgrade Version

Choose the specific Java upgrade option that matches your target version. Bob will present you with available upgrade paths based on your current Java version and project requirements.

![Java upgrade](image/12-java-upgrade.png)

Bob will start to create a to-do list and install the dependencies.

![Java upgrade progress](image/12.1-java-upgrade.png)

### Step 7: Review Upgrade Plan

Bob will create a comprehensive to-do list outlining all the tasks required for the upgrade. This includes updating dependencies, modifying deprecated code, updating configuration files, and ensuring compatibility with the new Java version.

![Java upgrade plan](image/12.2-java-upgrade.png)

### Step 8: Monitor Upgrade Progress

Watch as Bob systematically executes each item on the to-do list.

![Perform agentic upgrade](image/13-perform-agentic-upgrade.png)

Bob will update files, refactor code, and make necessary changes to ensure your application works with the upgraded Java version. You can monitor the progress in real-time.

![Progressing upgrade](image/14-progressing-upgrade.png)

### Step 9: Review and Approve Changes

Once Bob completes the upgrade tasks, review the changes made to your codebase. Bob will present a summary of all modifications. Carefully review these changes and approve them if everything looks correct.

![Approve Java](image/15-approve-java.png)

### Step 10: Post-Approval Processing

After your approval, Bob will finalize the upgrade process. This includes running any post-upgrade scripts, validating the changes, and ensuring all files are properly updated.

![Java upgrade approved](image/16-java-upgrade.png)

### Step 11: Complete the Build

Bob will complete the build process, ensuring that your upgraded application compiles successfully. This step verifies that all dependencies are resolved and the code is ready for testing.

![Finish upgrade](image/17-finish-upgrade-java.png)

### Step 12: Review Generated Documentation

Bob automatically generates comprehensive documentation for the upgrade process.

![Create documentation](image/18-create-documentation.png)

This documentation includes details about what was changed, why it was changed, and any important notes for developers.

![Documentation Java update](image/19-documentation-java-update.png)

### Step 13: View Mermaid Diagram

Bob creates a visual Mermaid diagram that illustrates the upgrade process, showing the flow of changes and dependencies.

![Documentation Java update](image/19.1-documentation-java-update.png)

![Documentation Java update](image/19.2-documentation-java-update.png)

This diagram helps team members understand the modernization journey at a glance.

![Documentation Java update](image/19.3-documentation-java-update.png)

### Step 14: Review Final Results

Review the final results of the Java upgrade. Bob provides a detailed summary showing the before and after state of your application, including version changes, updated dependencies, and performance improvements.

![Results Java](image/20-results-java.png)

You can also preview code changes and review the diff between the old and new versions of your application.

![Results Java](image/20.1-results-java.png)

### Step 15: Push to Your GitHub Fork

Once you're satisfied with the upgrade results, push the changes to **your forked repository** on GitHub. Bob can assist with creating a proper commit message that describes all the changes made during the modernization process.

**Important:** These changes will be pushed to your personal fork, not the original repository. This ensures your work doesn't affect other participants.

```bash
git add .
git commit -m "Java modernization: Upgraded to Java [version]"
git push origin main
```

![Push to Git](image/21-push-git.png)

### Step 16: Concert Scan

After pushing to GitHub, the changes will be automatically scanned by Concert for security vulnerabilities and code quality issues. Concert provides an additional layer of validation to ensure your modernized code meets security and quality standards.

![GitHub results](image/22-github.png)

## Conclusion

Congratulations! You have successfully modernized your Java application using Bob.

## Next Steps

- Setup Personal Acces Token GitHub
- Setup Concert Scan
- Java application scanned by Concert