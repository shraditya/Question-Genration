#!/bin/bash

# Revert to Original Frontend
# This script restores your original files

echo "↩️  Reverting to original frontend..."
echo ""

cd frontend/src

# Check if backups exist
if [ ! -f "App_Original_Backup.jsx" ]; then
    echo "❌ No backups found. Cannot revert."
    echo "   Backups should be: App_Original_Backup.jsx"
    exit 1
fi

# Restore original files
echo "📦 Restoring from backups..."
cp App_Original_Backup.jsx App.jsx
echo "   ✅ App.jsx restored"

if [ -f "pages/AutoTag_Original_Backup.jsx" ]; then
    cp pages/AutoTag_Original_Backup.jsx pages/AutoTag.jsx
    echo "   ✅ AutoTag.jsx restored"
fi

if [ -f "pages/SimilarityCheck_Original_Backup.jsx" ]; then
    cp pages/SimilarityCheck_Original_Backup.jsx pages/SimilarityCheck.jsx
    echo "   ✅ SimilarityCheck.jsx restored"
fi

echo ""
echo "✅ Successfully reverted to original frontend!"
echo ""
echo "🚀 Restart your dev server: npm run dev"
