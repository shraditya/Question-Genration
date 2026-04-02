#!/bin/bash

# Activate All Frontend Enhancements
# This script switches your app to the enhanced version

echo "🎨 Activating Frontend Enhancements..."
echo ""

cd frontend/src

# 1. Backup original files
echo "📦 Creating backups..."
cp App.jsx App_Original_Backup.jsx
cp pages/AutoTag.jsx pages/AutoTag_Original_Backup.jsx 2>/dev/null || true
cp pages/SimilarityCheck.jsx pages/SimilarityCheck_Original_Backup.jsx 2>/dev/null || true

# 2. Activate new sidebar layout
echo "✨ Activating sidebar layout..."
cp App_New.jsx App.jsx

# 3. Activate Smart Tagging
echo "🏷️  Activating Smart Tagging page..."
if [ -f "pages/SmartTagging.jsx" ]; then
    cp pages/SmartTagging.jsx pages/AutoTag.jsx
    echo "   ✅ Smart Tagging activated"
else
    echo "   ⚠️  SmartTagging.jsx not found, keeping original"
fi

# 4. Activate Enhanced Duplicate Detection
echo "🔍 Activating Enhanced Duplicate Detection..."
if [ -f "pages/EnhancedDuplicateDetection.jsx" ]; then
    cp pages/EnhancedDuplicateDetection.jsx pages/SimilarityCheck.jsx
    echo "   ✅ Duplicate Detection activated"
else
    echo "   ⚠️  EnhancedDuplicateDetection.jsx not found, keeping original"
fi

echo ""
echo "✅ All enhancements activated!"
echo ""
echo "📝 Backups saved as:"
echo "   - App_Original_Backup.jsx"
echo "   - AutoTag_Original_Backup.jsx"
echo "   - SimilarityCheck_Original_Backup.jsx"
echo ""
echo "🚀 Next steps:"
echo "   1. Restart your dev server: npm run dev"
echo "   2. Open http://localhost:3000"
echo "   3. Enjoy your new modern UI!"
echo ""
echo "💡 To revert: ./revert_enhancements.sh"
