#!/bin/bash

# Raposa Domain Checker - Git Workflow Helper Scripts
# Streamlined git operations for development workflow

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[GIT] $1${NC}"; }
warn() { echo -e "${YELLOW}[WARN] $1${NC}"; }
error() { echo -e "${RED}[ERROR] $1${NC}"; }
info() { echo -e "${BLUE}[INFO] $1${NC}"; }

# Quick commit with formatted message
quick_commit() {
    if [ -z "$1" ]; then
        error "Please provide a commit message"
        echo "Usage: $0 commit \"Your commit message\""
        exit 1
    fi
    
    log "Quick commit with message: $1"
    
    # Add all changes
    git add .
    
    # Show what will be committed
    info "Files to be committed:"
    git diff --cached --name-only
    echo ""
    
    # Commit with message
    git commit -m "$1"
    
    log "Commit created successfully!"
}

# Start new feature branch
new_feature() {
    if [ -z "$1" ]; then
        error "Please provide a feature name"
        echo "Usage: $0 feature feature-name"
        exit 1
    fi
    
    feature_name="feature/$1"
    
    log "Creating new feature branch: $feature_name"
    
    # Ensure we're on develop
    git checkout develop
    git pull origin develop
    
    # Create and checkout feature branch
    git checkout -b "$feature_name"
    
    log "Feature branch '$feature_name' created and checked out!"
    info "When ready, use: $0 finish-feature"
}

# Finish feature and merge to develop
finish_feature() {
    current_branch=$(git branch --show-current)
    
    if [[ ! "$current_branch" =~ ^feature/ ]]; then
        error "Not on a feature branch. Current branch: $current_branch"
        exit 1
    fi
    
    log "Finishing feature branch: $current_branch"
    
    # Ensure all changes are committed
    if [ -n "$(git status --porcelain)" ]; then
        warn "You have uncommitted changes:"
        git status --short
        read -p "Commit them now? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "Enter commit message: " commit_msg
            quick_commit "$commit_msg"
        else
            error "Please commit or stash changes first"
            exit 1
        fi
    fi
    
    # Switch to develop and merge
    git checkout develop
    git pull origin develop
    git merge "$current_branch"
    
    # Push to origin
    git push origin develop
    
    # Delete feature branch
    git branch -d "$current_branch"
    git push origin --delete "$current_branch" 2>/dev/null || true
    
    log "Feature merged to develop and branch deleted!"
}

# Quick sync with remote
sync() {
    current_branch=$(git branch --show-current)
    log "Syncing branch '$current_branch' with remote..."
    
    # Stash any uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        warn "Stashing uncommitted changes..."
        git stash push -m "Auto-stash before sync"
        stashed=true
    else
        stashed=false
    fi
    
    # Pull latest changes
    git pull origin "$current_branch"
    
    # Restore stashed changes
    if [ "$stashed" = true ]; then
        info "Restoring stashed changes..."
        git stash pop
    fi
    
    log "Sync complete!"
}

# Release to production (develop -> main)
release() {
    log "Starting release process (develop -> main)..."
    
    # Ensure develop is clean and up-to-date
    git checkout develop
    
    if [ -n "$(git status --porcelain)" ]; then
        error "Develop branch has uncommitted changes. Please commit first."
        git status --short
        exit 1
    fi
    
    git pull origin develop
    
    # Switch to main and merge
    git checkout main
    git pull origin main
    git merge develop
    
    # Push to trigger production deployment
    git push origin main
    
    log "Release complete! Production deployment triggered."
    info "Monitor deployment at Railway dashboard"
}

# Quick status check
status() {
    log "Git Status Summary:"
    echo ""
    
    info "Current branch: $(git branch --show-current)"
    info "Last commit: $(git log -1 --oneline)"
    echo ""
    
    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        warn "Uncommitted changes:"
        git status --short
    else
        info "Working tree clean ✅"
    fi
    echo ""
    
    # Check if branch is behind remote
    git fetch origin 2>/dev/null
    current_branch=$(git branch --show-current)
    behind=$(git rev-list --count HEAD..origin/"$current_branch" 2>/dev/null || echo "0")
    ahead=$(git rev-list --count origin/"$current_branch"..HEAD 2>/dev/null || echo "0")
    
    if [ "$behind" -gt 0 ]; then
        warn "Branch is $behind commits behind origin"
    fi
    
    if [ "$ahead" -gt 0 ]; then
        info "Branch is $ahead commits ahead of origin"
    fi
    
    if [ "$behind" -eq 0 ] && [ "$ahead" -eq 0 ]; then
        info "Branch is up to date with origin ✅"
    fi
}

# Clean up merged branches
cleanup() {
    log "Cleaning up merged branches..."
    
    # Switch to develop
    git checkout develop
    
    # Delete merged feature branches
    merged_branches=$(git branch --merged | grep -E "feature/" | grep -v "\*" || true)
    
    if [ -n "$merged_branches" ]; then
        info "Deleting merged feature branches:"
        echo "$merged_branches"
        echo "$merged_branches" | xargs -n 1 git branch -d
        
        # Try to delete remote branches too
        echo "$merged_branches" | xargs -n 1 -I {} git push origin --delete {} 2>/dev/null || true
    else
        info "No merged feature branches to clean up"
    fi
    
    log "Cleanup complete!"
}

# Show recent commits
history() {
    count=${1:-10}
    log "Recent $count commits:"
    git log --oneline -n "$count" --graph --decorate
}

# Show branches
branches() {
    log "Local branches:"
    git branch -v
    echo ""
    
    log "Remote branches:"
    git branch -rv
}

# Undo last commit (keep changes)
undo_commit() {
    log "Undoing last commit (keeping changes)..."
    git reset --soft HEAD~1
    log "Last commit undone. Changes are still staged."
}

# Emergency stash and sync
emergency_sync() {
    log "Emergency sync - stashing everything and pulling latest..."
    
    # Stash everything including untracked files
    git stash push -u -m "Emergency stash $(date)"
    
    # Sync with remote
    sync
    
    log "Emergency sync complete. Use 'git stash list' to see stashed changes."
}

# Show help
show_help() {
    echo "Raposa Domain Checker - Git Workflow Helper"
    echo ""
    echo "Usage: $0 <command> [arguments]"
    echo ""
    echo "Commands:"
    echo "  commit <msg>        Quick commit all changes with message"
    echo "  feature <name>      Start new feature branch from develop"
    echo "  finish-feature      Finish current feature and merge to develop"
    echo "  sync                Sync current branch with remote"
    echo "  release             Release develop to main (triggers production)"
    echo "  status              Show git status summary"
    echo "  cleanup             Clean up merged feature branches"
    echo "  history [count]     Show recent commits (default: 10)"
    echo "  branches            Show all branches"
    echo "  undo                Undo last commit (keep changes)"
    echo "  emergency           Emergency stash and sync"
    echo "  help                Show this help message"
    echo ""
    echo "Workflow Examples:"
    echo "  $0 feature user-auth    # Start new feature"
    echo "  $0 commit \"Add login\"   # Quick commit"
    echo "  $0 finish-feature       # Merge to develop"
    echo "  $0 release              # Deploy to production"
    echo ""
    echo "Branch Strategy:"
    echo "  develop → Development environment (stage.domainchecker.raposa.tech)"
    echo "  main    → Production environment (api.domainchecker.raposa.tech)"
}

# Main script logic
main() {
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        error "Not in a git repository"
        exit 1
    fi
    
    case "${1:-help}" in
        "commit")
            quick_commit "$2"
            ;;
        "feature")
            new_feature "$2"
            ;;
        "finish-feature")
            finish_feature
            ;;
        "sync")
            sync
            ;;
        "release")
            release
            ;;
        "status")
            status
            ;;
        "cleanup")
            cleanup
            ;;
        "history")
            history "$2"
            ;;
        "branches")
            branches
            ;;
        "undo")
            undo_commit
            ;;
        "emergency")
            emergency_sync
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

main "$@"
