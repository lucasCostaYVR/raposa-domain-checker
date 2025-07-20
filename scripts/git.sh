#!/bin/bash

# Git Workflow Script for FastAPI Projects
# Streamlined git operations and branch management

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}[GIT]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

show_help() {
    echo "Git Workflow for FastAPI"
    echo ""
    echo "Usage: ./scripts/git.sh [command] [args]"
    echo ""
    echo "Commands:"
    echo "  status             Show comprehensive git status"
    echo "  sync               Sync with remote safely"
    echo "  feature <name>     Create and switch to feature branch"
    echo "  commit <message>   Quick commit with proper formatting"
    echo "  push               Push current branch to remote"
    echo "  cleanup            Clean up merged branches"
    echo "  log                Show recent commits with nice formatting"
    echo "  undo               Undo last commit (keep changes)"
    echo "  reset              Reset to last remote state (WARNING: loses changes)"
    echo ""
}

check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not in a git repository"
        exit 1
    fi
}

show_status() {
    print_step "Git repository status"
    echo ""
    
    # Current branch
    echo "🌿 Current branch: $(git branch --show-current)"
    
    # Remote status
    git fetch --quiet
    AHEAD=$(git rev-list --count HEAD..@{u} 2>/dev/null || echo "0")
    BEHIND=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo "0")
    
    if [ "$AHEAD" -gt 0 ]; then
        echo "⬇️  Behind remote by $AHEAD commits"
    fi
    
    if [ "$BEHIND" -gt 0 ]; then
        echo "⬆️  Ahead of remote by $BEHIND commits"
    fi
    
    if [ "$AHEAD" -eq 0 ] && [ "$BEHIND" -eq 0 ]; then
        echo "✅ Up to date with remote"
    fi
    
    echo ""
    
    # Working directory status
    if git diff-index --quiet HEAD --; then
        print_success "Working directory clean"
    else
        print_warning "You have uncommitted changes:"
        git status --porcelain
    fi
    
    echo ""
    echo "📋 Recent commits:"
    git log --oneline -5
}

sync_with_remote() {
    print_step "Syncing with remote..."
    
    CURRENT_BRANCH=$(git branch --show-current)
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        print_warning "You have uncommitted changes"
        read -p "Stash changes and continue? (y/n): " stash_changes
        if [ "$stash_changes" = "y" ]; then
            git stash push -m "Auto-stash before sync"
            STASHED=true
        else
            print_error "Cannot sync with uncommitted changes"
            exit 1
        fi
    fi
    
    # Fetch and merge
    git fetch origin
    git merge origin/"$CURRENT_BRANCH"
    
    # Restore stashed changes if any
    if [ "${STASHED:-false}" = "true" ]; then
        print_step "Restoring stashed changes..."
        git stash pop
    fi
    
    print_success "Synced with remote"
}

create_feature() {
    if [ -z "$1" ]; then
        print_error "Feature name required"
        echo "Usage: ./scripts/git.sh feature <name>"
        exit 1
    fi
    
    FEATURE_NAME="feature/$1"
    
    print_step "Creating feature branch: $FEATURE_NAME"
    
    # Ensure we're on main/master
    git checkout main 2>/dev/null || git checkout master 2>/dev/null || {
        print_error "Could not switch to main/master branch"
        exit 1
    }
    
    # Sync with remote
    git pull origin
    
    # Create and switch to feature branch
    git checkout -b "$FEATURE_NAME"
    
    print_success "Created and switched to $FEATURE_NAME"
    echo "💡 When ready, commit your changes and push with:"
    echo "   ./scripts/git.sh commit \"Your commit message\""
    echo "   ./scripts/git.sh push"
}

quick_commit() {
    if [ -z "$1" ]; then
        print_error "Commit message required"
        echo "Usage: ./scripts/git.sh commit \"Your commit message\""
        exit 1
    fi
    
    # Check if there are changes to commit
    if git diff-index --quiet HEAD --; then
        print_warning "No changes to commit"
        exit 0
    fi
    
    print_step "Committing changes..."
    
    # Show what will be committed
    echo "Changes to be committed:"
    git diff --name-status --cached
    
    if [ -z "$(git diff --name-only --cached)" ]; then
        print_step "Adding all changes..."
        git add .
    fi
    
    # Commit with message
    git commit -m "$1"
    
    print_success "Changes committed"
    echo "📝 Commit: $1"
    
    # Suggest next steps
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
        echo ""
        echo "💡 Next steps:"
        echo "   ./scripts/git.sh push     # Push to remote"
    fi
}

push_branch() {
    CURRENT_BRANCH=$(git branch --show-current)
    
    print_step "Pushing $CURRENT_BRANCH to remote..."
    
    # Check if remote branch exists
    if git ls-remote --exit-code --heads origin "$CURRENT_BRANCH" > /dev/null 2>&1; then
        git push origin "$CURRENT_BRANCH"
    else
        print_step "Setting up remote tracking..."
        git push -u origin "$CURRENT_BRANCH"
    fi
    
    print_success "Pushed to remote"
    
    # Show GitHub URL if possible
    REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
    if [[ "$REMOTE_URL" == *"github.com"* ]]; then
        REPO_PATH=$(echo "$REMOTE_URL" | sed 's/.*github\.com[:/]\([^/]*\/[^/]*\)\.git/\1/')
        echo ""
        echo "🔗 Create pull request:"
        echo "   https://github.com/$REPO_PATH/compare/$CURRENT_BRANCH"
    fi
}

cleanup_branches() {
    print_step "Cleaning up merged branches..."
    
    # Switch to main/master
    git checkout main 2>/dev/null || git checkout master 2>/dev/null
    
    # Sync with remote
    git pull origin
    
    # Delete merged branches
    MERGED_BRANCHES=$(git branch --merged | grep -v '\*\|main\|master' | tr -d ' ')
    
    if [ -z "$MERGED_BRANCHES" ]; then
        print_success "No merged branches to clean up"
        return
    fi
    
    echo "Merged branches to delete:"
    echo "$MERGED_BRANCHES"
    echo ""
    read -p "Delete these branches? (y/n): " confirm_delete
    
    if [ "$confirm_delete" = "y" ]; then
        echo "$MERGED_BRANCHES" | xargs -n 1 git branch -d
        print_success "Cleaned up merged branches"
    fi
}

show_log() {
    print_step "Recent commit history"
    echo ""
    git log --oneline --graph --decorate -10
}

undo_commit() {
    print_step "Undoing last commit (keeping changes)..."
    
    LAST_COMMIT=$(git log -1 --oneline)
    echo "Last commit: $LAST_COMMIT"
    
    read -p "Undo this commit? (y/n): " confirm_undo
    
    if [ "$confirm_undo" = "y" ]; then
        git reset --soft HEAD~1
        print_success "Commit undone, changes kept in staging"
    fi
}

reset_to_remote() {
    print_warning "This will LOSE all local changes!"
    CURRENT_BRANCH=$(git branch --show-current)
    echo "Branch: $CURRENT_BRANCH"
    
    read -p "Are you sure? Type 'yes' to confirm: " confirm_reset
    
    if [ "$confirm_reset" = "yes" ]; then
        git fetch origin
        git reset --hard origin/"$CURRENT_BRANCH"
        git clean -fd
        print_success "Reset to remote state"
    else
        print_step "Reset cancelled"
    fi
}

# Main command handling
check_git_repo

case "${1:-}" in
    "status")
        show_status
        ;;
    "sync")
        sync_with_remote
        ;;
    "feature")
        create_feature "$2"
        ;;
    "commit")
        quick_commit "$2"
        ;;
    "push")
        push_branch
        ;;
    "cleanup")
        cleanup_branches
        ;;
    "log")
        show_log
        ;;
    "undo")
        undo_commit
        ;;
    "reset")
        reset_to_remote
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    "")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
