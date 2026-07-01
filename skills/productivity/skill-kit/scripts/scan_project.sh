#!/usr/bin/env bash
# scan_project.sh — Phase 1 project discovery for the skill-kit skill.
#
# Scans a project folder (a code repo OR a plain folder of files) and prints a
# structured profile: detected stack, config/infra signals, likely domain,
# non-code folder type, capability GAPS, and suggested find-skills queries.
#
# It is a fast FIRST pass, not the last word — the skill reads these findings
# and applies judgement. Deliberately dependency-free: POSIX tools only, no jq,
# no network. Values emitted in --json are controlled tokens (known filenames /
# query strings with no quotes or backslashes), so the hand-built JSON is valid.
#
# Usage:
#   bash scripts/scan_project.sh [dir] [--depth N] [--json]
#   dir      folder to scan (default: .)
#   --depth  how many levels deep to descend (default: 3)
#   --json   emit machine-readable JSON instead of the formatted report

set -uo pipefail

DIR="." ; DEPTH=3 ; JSON=0
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) awk 'NR==1{next} /^#/{sub(/^# ?/,"");print;next} {exit}' "$0"; exit 0 ;;
    --depth) DEPTH="${2:-3}"; shift 2 ;;
    --json)  JSON=1; shift ;;
    *)       DIR="$1"; shift ;;
  esac
done
case "$DEPTH" in ''|*[!0-9]*) DEPTH=3 ;; esac
[ -d "$DIR" ] || { echo "error: not a directory: $DIR" >&2; exit 1; }

PRUNE='-name .git -o -name node_modules -o -name vendor -o -name dist -o -name build -o -name .next -o -name .nuxt -o -name __pycache__ -o -name .venv -o -name venv -o -name target -o -name .gradle -o -name .idea -o -name .cache -o -name coverage'

# All scanned files, honoring depth and the prune list.
ALLFILES="$(find "$DIR" -mindepth 1 -maxdepth "$DEPTH" \( $PRUNE \) -prune -o -type f -print 2>/dev/null)"

# have <regex-over-paths> : true if any scanned path matches.
have() { printf '%s\n' "$ALLFILES" | grep -Eq "$1"; }
# Dependency/manifest files, then dep() greps them for a library pattern.
MANIFESTS="$(printf '%s\n' "$ALLFILES" | grep -Ei '/(package\.json|requirements\.txt|pyproject\.toml|setup\.py|Pipfile|Cargo\.toml|go\.mod|Gemfile|composer\.json|pom\.xml|build\.gradle[^/]*)$' || true)"
dep() { [ -n "$MANIFESTS" ] && printf '%s\n' "$MANIFESTS" | tr '\n' '\0' | xargs -0 grep -liE "$1" 2>/dev/null | grep -q .; }

# Accumulators. STACK/FW/INFRA are space-joined single tokens; GAPS and QUERIES
# are NEWLINE-joined so multi-word queries ("posthog analytics") stay intact.
STACK="" ; FW="" ; INFRA="" ; GAPS="" ; QUERIES=""
add()  { eval "$1=\"\${$1:+\${$1} }$2\""; }                       # space-join
addg() { GAPS="${GAPS:+$GAPS$'\n'}$1"; }                          # newline-join gap
addq() { QUERIES="${QUERIES:+$QUERIES$'\n'}$1"; }                 # newline-join query
gap()  { addg "$1"; addq "$2"; }

# ---- stack / frameworks --------------------------------------------------
have '/package\.json$'                                          && add STACK "node/javascript"
have '/(requirements\.txt|pyproject\.toml|setup\.py|Pipfile)$'  && add STACK "python"
have '/Cargo\.toml$'                                            && add STACK "rust"
have '/go\.mod$'                                                && add STACK "go"
have '/Gemfile$'                                                && add STACK "ruby"
have '/composer\.json$'                                         && add STACK "php"
have '/(pom\.xml|build\.gradle[^/]*)$'                          && add STACK "jvm/java"

dep 'next'                                         && add FW "next.js"
dep '"react"'                                      && add FW "react"
dep 'vue'                                          && add FW "vue"
dep 'svelte'                                       && add FW "svelte"
dep 'express|fastify|koa|nest'                     && add FW "node-server"
dep 'django'                                       && add FW "django"
dep 'flask|fastapi'                                && add FW "python-web"
dep 'pandas|numpy|jupyter|scikit|torch|tensorflow' && add FW "data/ml"

# ---- config / infra signals ---------------------------------------------
have '/next\.config\.'     && add INFRA "next-config"
have '/vite\.config\.'     && add INFRA "vite"
have '/tailwind\.config\.' && add INFRA "tailwind"
have '/Dockerfile$'        && add INFRA "docker"
have '/vercel\.json$'      && add INFRA "vercel"
have '/\.env(\.example)?$' && add INFRA "env-config"

# ---- code vs non-code, and folder classification -------------------------
# A detected manifest/stack means this is a code project; the code-hygiene gaps
# (tests, CI, lint) only make sense there. With no stack, treat it as a folder
# of files (the non-developer case) and classify it by what dominates.
is_code=0; [ -n "$STACK" ] && is_code=1
is_web=0
case " $FW " in *" next.js "*|*" react "*|*" vue "*|*" svelte "*|*" node-server "*|*" django "*|*" python-web "*) is_web=1 ;; esac

EXT_TOP="$(printf '%s\n' "$ALLFILES" | sed -n 's/.*\.\([A-Za-z0-9]\{1,5\}\)$/\1/p' | tr 'A-Z' 'a-z' | sort | uniq -c | sort -rn | head -6 | awk '{print $2"("$1")"}' | tr '\n' ' ')"
FOLDER_TYPE=""
if [ "$is_code" = 0 ]; then
  DOC_N="$(printf '%s\n' "$ALLFILES"   | grep -Eic '\.(docx?|pdf|txt|md|rtf|pptx?)$' || true)"
  SHEET_N="$(printf '%s\n' "$ALLFILES" | grep -Eic '\.(xlsx?|csv|numbers)$' || true)"
  IMG_N="$(printf '%s\n' "$ALLFILES"   | grep -Eic '\.(png|jpe?g|gif|svg|psd|ai|fig|sketch|xd)$' || true)"
  biggest=${SHEET_N:-0}; FOLDER_TYPE="spreadsheets / accounting / data"
  [ "${DOC_N:-0}" -gt "$biggest" ] && { biggest=$DOC_N; FOLDER_TYPE="documents / content archive / research notes"; }
  [ "${IMG_N:-0}" -gt "$biggest" ] && { biggest=$IMG_N; FOLDER_TYPE="design project / image assets"; }
  [ "${biggest:-0}" -eq 0 ] && FOLDER_TYPE=""
fi

# ---- capability GAPS -----------------------------------------------------
# A gap = a capability the project plausibly wants but shows no sign of.
if [ "$is_code" = 1 ]; then
  dep 'posthog|@vercel/analytics|gtag|google-analytics|mixpanel|segment|plausible|amplitude' \
    || { [ "$is_web" = 1 ] && gap "no-analytics" "posthog analytics"; }

  # Payment integration present but provider possibly unspecified → a likely CRITICAL question.
  if dep 'stripe|paddle|braintree|lemonsqueezy|paypal'; then
    addg "payments-present(confirm-provider)"; addq "stripe payments"
  elif [ "$is_web" = 1 ] && have '/(cart|checkout|pricing)'; then
    gap "checkout-no-provider" "stripe payments"
  fi

  { have '/(test|tests|__tests__|spec|__test__)/' || dep 'jest|vitest|mocha|playwright|cypress|@testing-library|pytest|rspec'; } \
    || gap "no-tests" "playwright e2e testing"
  have '/(\.github/workflows|\.gitlab-ci\.yml|\.circleci|azure-pipelines\.yml|Jenkinsfile)' \
    || gap "no-ci" "github actions ci"
  { have '/(\.eslintrc|\.prettierrc|\.editorconfig|ruff\.toml|\.rubocop\.yml)' || dep 'eslint|prettier|ruff|black|flake8|rubocop'; } \
    || gap "no-lint-format" "eslint prettier setup"
  dep 'sentry|@sentry|bugsnag|rollbar|datadog' \
    || { [ "$is_web" = 1 ] && gap "no-error-monitoring" "sentry error monitoring"; }
  if [ "$is_web" = 1 ]; then
    dep 'next-auth|@auth|passport|clerk|@clerk|auth0|lucia|firebase' || gap "no-auth" "authentication setup"
    dep 'i18next|next-intl|react-intl|vue-i18n'                      || gap "maybe-no-i18n" "internationalization i18n"
    dep 'axe|jsx-a11y|next-seo|react-helmet'                         || gap "maybe-no-a11y-seo" "accessibility audit"
  fi
  have '/(README|readme)' || gap "no-readme" "readme documentation"

  # Stack-shaped performance query.
  case " $FW " in *" next.js "*) addq "next.js performance" ;; *" react "*) addq "react performance" ;; esac
else
  # Non-code folder: suggest domain skills that fit what the folder holds,
  # not code-project hygiene the user has no use for.
  case "$FOLDER_TYPE" in
    spreadsheets*) gap "spreadsheet-tasks" "spreadsheet analysis";  addq "data analysis" ;;
    documents*)    gap "document-tasks"    "document processing";   addq "pdf editing" ;;
    design*)       gap "design-tasks"      "image editing";         addq "design assets" ;;
    *)             addg "unclassified-folder — inspect it and ask the user what it's for" ;;
  esac
fi

# ---- domain guess (modest heuristic) -------------------------------------
DOMAIN="unknown"
if dep 'stripe|paddle|braintree|lemonsqueezy'; then DOMAIN="e-commerce / payments"
elif case " $FW " in *" data/ml "*) true ;; *) false ;; esac; then DOMAIN="data / ml pipeline"
elif dep 'next-mdx|contentlayer|gatsby' || have '/(content|posts|blog)/'; then DOMAIN="content / marketing site"
elif [ "$is_web" = 1 ]; then DOMAIN="web application"
elif [ -n "$FOLDER_TYPE" ]; then DOMAIN="non-code: $FOLDER_TYPE"
fi

# ---- output --------------------------------------------------------------
# JSON array from a newline-delimited list (skips blanks; inputs are quote-free).
jarr_nl() {
  local first=1 line out=""
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    if [ $first = 1 ]; then out="\"$line\""; first=0; else out="$out,\"$line\""; fi
  done <<EOF
$1
EOF
  printf '[%s]' "$out"
}
# JSON array from a space-delimited token list.
jarr_sp() {
  local first=1 tok out=""
  for tok in $1; do
    if [ $first = 1 ]; then out="\"$tok\""; first=0; else out="$out,\"$tok\""; fi
  done
  printf '[%s]' "$out"
}

if [ "$JSON" = 1 ]; then
  printf '{\n'
  printf '  "dir": "%s",\n'          "$DIR"
  printf '  "stack": %s,\n'          "$(jarr_sp "$STACK")"
  printf '  "frameworks": %s,\n'     "$(jarr_sp "$FW")"
  printf '  "infra": %s,\n'          "$(jarr_sp "$INFRA")"
  printf '  "domain": "%s",\n'       "$DOMAIN"
  printf '  "folder_type": "%s",\n'  "$FOLDER_TYPE"
  printf '  "gaps": %s,\n'           "$(jarr_nl "$GAPS")"
  printf '  "suggested_queries": %s\n' "$(jarr_nl "$QUERIES")"
  printf '}\n'
  exit 0
fi

echo "PROJECT PROFILE  —  $DIR  (depth $DEPTH)"
echo "-------------------------------------------------------------"
echo "  stack        : ${STACK:-none detected}"
echo "  frameworks   : ${FW:-none detected}"
echo "  infra/config : ${INFRA:-none detected}"
echo "  domain guess : $DOMAIN"
[ -n "$FOLDER_TYPE" ] && echo "  folder type  : $FOLDER_TYPE (looks non-code)"
echo "  top ext      : ${EXT_TOP:-none}"
echo
echo "  CAPABILITY GAPS (candidate needs):"
if [ -n "$GAPS" ]; then printf '%s\n' "$GAPS" | while IFS= read -r g; do [ -n "$g" ] && echo "    - $g"; done
else echo "    (none obvious — read the folder yourself)"; fi
echo
echo "  SUGGESTED find-skills QUERIES:"
if [ -n "$QUERIES" ]; then printf '%s\n' "$QUERIES" | while IFS= read -r q; do [ -n "$q" ] && echo "    - $q"; done
else echo "    (derive from stack + gaps in Phase 3)"; fi
echo
echo "  NOTE: heuristic first pass — confirm against what you can see before Phase 3."
