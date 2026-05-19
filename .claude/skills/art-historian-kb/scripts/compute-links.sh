#!/usr/bin/env bash
# Compute bidirectional links between art historians
# Builds relationship graph from all records

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

SOURCE_DIR="${PROJECT_ROOT}/01-RwaFiles/art_historians_json"
LINK_GRAPH="${PROJECT_ROOT}/.processing/link-graph.json"
PROCESSING_DIR="${PROJECT_ROOT}/.processing"

# Weights
WEIGHT_INSTITUTIONAL=0.8
WEIGHT_TEMPORAL=0.6
WEIGHT_SUBJECT=0.7
WEIGHT_BIBLIOGRAPHIC=0.9
WEIGHT_TEXTUAL=0.4

# Threshold
THRESHOLD=0.5

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

usage() {
    cat << 'EOF'
Usage: compute-links.sh [OPTIONS]

Options:
    --all         Compute all links (full rebuild)
    --scholar     Update links for single scholar
    --force       Ignore cache, recompute all
    -h, --help    Show this help

Examples:
    ./compute-links.sh --all
    ./compute-links.sh --scholar abbottj
EOF
}

# Extract institutions from text
extract_institutions() {
    local text="$1"
    # Common institutions to look for
    local institutions=(
        "Harvard" "Yale" "Princeton" "Columbia" "MIT" "Stanford"
        "Museum of Modern Art" "MoMA" "Metropolitan Museum"
        "Smith College" "Bowdoin" "University" "Institute"
        "Louvre" "British Museum" "National Gallery"
    )
    local found=()

    for inst in "${institutions[@]}"; do
        if echo "$text" | grep -qi "$inst"; then
            found+=("$inst")
        fi
    done

    printf '%s\n' "${found[@]}"
}

# Extract time period
get_time_period() {
    local birth="$1"
    local death="$2"

    if [ -z "$birth" ]; then
        echo "unknown"
        return
    fi

    local decade=$((birth / 10 * 10))
    echo "${decade}s"
}

# Compute link score between two scholars
compute_link_score() {
    local json_a="$1"
    local json_b="$2"

    local name_a=$(echo "$json_a" | jq -r '.Full Name // .Title // empty')
    local name_b=$(echo "$json_b" | jq -r '.Full Name // .Title // empty')
    local birth_a=$(echo "$json_a" | jq -r '.Birth Year // empty')
    local birth_b=$(echo "$json_b" | jq -r '.Birth Year // empty')
    local death_a=$(echo "$json_a" | jq -r '.Death Year // empty')
    local death_b=$(echo "$json_b" | jq -r '.Death Year // empty')
    local subject_a=$(echo "$json_a" | jq -r '.Subject Area // empty')
    local subject_b=$(echo "$json_b" | jq -r '.Subject Area // empty')
    local overview_a=$(echo "$json_a" | jq -r '.Overview // empty')
    local overview_b=$(echo "$json_b" | jq -r '.Overview // empty')
    local sources_a=$(echo "$json_a" | jq -r '.Sources // empty')
    local sources_b=$(echo "$json_b" | jq -r '.Sources // empty')

    local score=0
    local reasons=()

    # Institutional connection
    local inst_a=$(extract_institutions "$overview_a $sources_a")
    local inst_b=$(extract_institutions "$overview_b $sources_b")
    for ia in $inst_a; do
        for ib in $inst_b; do
            if [ "$ia" = "$ib" ]; then
                score=$(echo "$score + $WEIGHT_INSTITUTIONAL" | bc)
                reasons+=("institutional: $ia")
            fi
        done
    done

    # Temporal proximity
    if [ -n "$birth_a" ] && [ -n "$birth_b" ]; then
        local diff=$((birth_a - birth_b))
        if [ ${diff#-} -le 10 ]; then
            score=$(echo "$score + $WEIGHT_TEMPORAL" | bc)
            reasons+=("temporal: ${birth_a}s vs ${birth_b}s")
        fi
    fi

    # Subject overlap
    if [ -n "$subject_a" ] && [ -n "$subject_b" ]; then
        local overlap=false
        IFS='|' read -ra SUBJ_A <<< "$subject_a"
        IFS='|' read -ra SUBJ_B <<< "$subject_b"
        for sa in "${SUBJ_A[@]}"; do
            for sb in "${SUBJ_B[@]}"; do
                if [ "${sa,,}" = "${sb,,}" ]; then
                    overlap=true
                    break 2
                fi
            done
        done
        if $overlap; then
            score=$(echo "$score + $WEIGHT_SUBJECT" | bc)
            reasons+=("subject overlap")
        fi
    fi

    # Bibliographic (source co-occurrence)
    if [ -n "$sources_a" ] && [ -n "$sources_b" ]; then
        for src in $sources_a; do
            if echo "$sources_b" | grep -q "$src"; then
                score=$(echo "$score + $WEIGHT_BIBLIOGRAPHIC" | bc)
                reasons+=("shared source")
                break
            fi
        done
    fi

    # Textual mention
    if echo "$overview_b" | grep -qi "$name_a"; then
        score=$(echo "$score + $WEIGHT_TEXTUAL" | bc)
        reasons+=("mentioned in overview")
    fi
    if echo "$overview_a" | grep -qi "$name_b"; then
        score=$(echo "$score + $WEIGHT_TEXTUAL" | bc)
        reasons+=("mentioned in overview")
    fi

    # Format output
    local score_str=$(printf "%.1f" "$score")
    local reasons_str=$(IFS=','; echo "${reasons[*]}")
    echo "$score_str|${reasons_str}"
}

# Load all records into memory
load_records() {
    local records=()

    for json_file in "${SOURCE_DIR}"/*.json; do
        if [ -f "$json_file" ]; then
            local shortcode=$(basename "$json_file" .json)
            local content=$(cat "$json_file")
            records+=("{\"shortcode\": \"$shortcode\", \"data\": $content}")
        fi
    done

    printf '%s\n' "${records[@]}" | jq -s '.'
}

# Compute all links
compute_all_links() {
    log_info "Loading records..."
    local records=$(load_records)
    local total=$(echo "$records" | jq 'length')
    log_info "Found $total scholars"

    local links=()
    local count=0
    local pair_count=0

    # Nested loop - O(n²)
    local record_array=$(echo "$records" | jq -c '.[]')
    for record_a in $record_array; do
        local shortcode_a=$(echo "$record_a" | jq -r '.shortcode')
        local data_a=$(echo "$record_a" | jq -r '.data')

        for record_b in $record_array; do
            local shortcode_b=$(echo "$record_b" | jq -r '.shortcode')

            # Skip self
            if [ "$shortcode_a" = "$shortcode_b" ]; then
                continue
            fi

            # Only compute for A < B (to avoid duplicates)
            if [[ "$shortcode_a" < "$shortcode_b" ]]; then
                ((pair_count++)) || true

                local data_b=$(echo "$record_b" | jq -r '.data')
                local result=$(compute_link_score "$data_a" "$data_b")
                local score=$(echo "$result" | cut -d'|' -f1)
                local reasons=$(echo "$result" | cut -d'|' -f2-)

                # Check threshold
                local meets_threshold=$(echo "$score >= $THRESHOLD" | bc)
                if [ "$meets_threshold" = "1" ]; then
                    links+=("{\"from\": \"$shortcode_a\", \"to\": \"$shortcode_b\", \"score\": $score, \"reasons\": \"$reasons\"}")
                fi
            fi
        done

        ((count++)) || true
        if [ $((count % 100)) -eq 0 ]; then
            log_info "Processed $count/$total scholars, $pair_count pairs, ${#links[@]} links found"
        fi
    done

    log_info "Computing complete. Processed $count scholars, $pair_count pairs, ${#links[@]} links found"

    # Write link graph
    mkdir -p "$PROCESSING_DIR"
    echo "{"
    echo "  \"computed_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
    echo "  \"total_scholars\": $total,"
    echo "  \"total_pairs\": $pair_count,"
    echo "  \"total_links\": ${#links[@]},"
    echo "  \"threshold\": $THRESHOLD,"
    echo "  \"links\": ["

    local first=true
    for link in "${links[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            echo ","
        fi
        echo -n "    $link"
    done

    echo ""
    echo "  ]"
    echo "}"
}

# Main
main() {
    local MODE="all"
    local SCHOLAR=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --all)
                MODE="all"
                shift
                ;;
            --scholar)
                MODE="single"
                SCHOLAR="$2"
                shift 2
                ;;
            --force)
                # TODO: implement cache busting
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                echo "Unknown: $1"
                usage
                exit 1
                ;;
        esac
    done

    case "$MODE" in
        all)
            compute_all_links > "$LINK_GRAPH"
            log_success "Link graph saved to: $LINK_GRAPH"
            ;;
        single)
            echo "Single scholar mode not yet implemented"
            exit 1
            ;;
    esac
}

main "$@"
