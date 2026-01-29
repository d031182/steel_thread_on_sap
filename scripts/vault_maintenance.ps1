# Knowledge Vault Maintenance Script
# Generated: 2026-01-29
# Purpose: Execute approved vault maintenance operations

Write-Host "="*80
Write-Host "Knowledge Vault Maintenance - Executing Approved Actions"
Write-Host "="*80
Write-Host ""

$ErrorActionPreference = "Stop"

# Phase 1: Delete obsolete files (22 files)
Write-Host "[Phase 1] Deleting 22 obsolete files..."

$filesToDelete = @(
    # Planning Archive (3)
    "docs/planning/archive/COMPLETE_VISION_EXECUTION_ROADMAP.md",
    "docs/planning/archive/MODULAR_REFACTORING_EXECUTION_PLAN.md",
    "docs/planning/archive/REUSABLE_MODULE_LIBRARY_VISION.md",
    
    # Planning Architecture (5)
    "docs/planning/architecture/FUTURE_PROOF_MODULE_ARCHITECTURE.md",
    "docs/planning/architecture/MODULAR_APPLICATION_ARCHITECTURE_PLAN.md",
    "docs/planning/architecture/POST_FLASK_REFACTORING_PLAN.md",
    "docs/planning/architecture/PROJECT_REORGANIZATION_PLAN.md",
    "docs/planning/architecture/PROJECT_STRUCTURE_REFACTORING_PLAN.md",
    
    # Planning Features (6)
    "docs/planning/features/API_PLAYGROUND_IMPLEMENTATION_PLAN.md",
    "docs/planning/features/CSN_VALIDATION_MODULE_REFACTORING_PLAN.md",
    "docs/planning/features/CSN_VIEWER_FINAL_IMPLEMENTATION_PLAN.md",
    "docs/planning/features/FIORI_CONTROL_SELECTION_GUIDE_TASK.md",
    "docs/planning/features/FIORI_UI5_DOCUMENTATION_SCRAPING_TASK.md",
    "docs/planning/features/TABLE_STRUCTURE_ENDPOINT_PLAN.md",
    
    # Planning Sessions (3)
    "docs/planning/sessions/GIT_TAGS_AND_CHECKPOINTS_GUIDE.md",
    "docs/planning/sessions/PROJECT_RESUMPTION_SESSION_2026-01-23.md",
    "docs/planning/sessions/ROLLBACK_POINT_SQLITE_LOGGING_COMPLETE.md",
    
    # Planning Summaries (3)
    "docs/planning/summaries/CSN_VALIDATION_RESULTS.md",
    "docs/planning/summaries/CSN_VALIDATION_SUMMARY.md",
    "docs/planning/summaries/APPLICATION_FEATURES.md",
    
    # Planning Root (2)
    "docs/planning/COMPREHENSIVE_FIORI_SAPUI5_SCRAPING_PLAN.md",
    "docs/planning/PLANNING_DOCS_ASSESSMENT.md"
)

$deleted = 0
foreach ($file in $filesToDelete) {
    if (Test-Path $file) {
        git rm $file 2>$null
        if ($?) {
            $deleted++
            Write-Host "  ✓ Deleted: $file"
        }
    }
}
Write-Host "  Deleted $deleted files"
Write-Host ""

# Phase 2: Remove empty folders
Write-Host "[Phase 2] Removing empty folders..."

$foldersToRemove = @(
    "docs/planning/archive",
    "docs/planning/architecture",
    "docs/planning/sessions"
)

$removed = 0
foreach ($folder in $foldersToRemove) {
    if ((Test-Path $folder) -and ((Get-ChildItem $folder).Count -eq 0)) {
        Remove-Item $folder -Force
        $removed++
        Write-Host "  ✓ Removed: $folder"
    }
}
Write-Host "  Removed $removed empty folders"
Write-Host ""

# Summary
Write-Host "="*80
Write-Host "Maintenance Complete!"
Write-Host "="*80
Write-Host "Files deleted: $deleted"
Write-Host "Folders removed: $removed"
Write-Host ""
Write-Host "Next: AI will integrate remaining 9 files with proper [[wikilinks]]"