# A set of common Bash functions useful for both suite runner and separate benchmark runners

ANSI_COLOR_RESET="\e[0m"
ANSI_COLOR_RED_FG="\e[31m"
ANSI_COLOR_GREEN_FG="\e[32m"
ANSI_COLOR_YELLOW_FG="\e[33m"
ANSI_COLOR_GRAY_FG="\e[90m"

CURRENT_SCRIPT_NAME="$(basename $0)"

if [[ "x$LOG_ENABLE_COLORS" == "x" ]]; then
    LOG_ENABLE_COLORS="yes"
fi

log () {
    local TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S.%3N%z')"
    local LEVEL="$1"
    local MESSAGE="$2"
    if [[ "x$LOG_ENABLE_COLORS" == "xyes" ]]; then
        local COLOR="$3"
        echo -e "($CURRENT_SCRIPT_NAME)\t $TIMESTAMP [$COLOR$LEVEL$ANSI_COLOR_RESET]\t$MESSAGE"
    else
        echo -e "($CURRENT_SCRIPT_NAME)\t $TIMESTAMP [$LEVEL]\t$MESSAGE"
    fi
}

fatal () {
    log "FATAL" "$1" "$ANSI_COLOR_RED_FG"
    exit 1
}

warn () {
    log "WARN" "$1" "$ANSI_COLOR_YELLOW_FG"
}

info () {
    log "INFO" "$1" "$ANSI_COLOR_GREEN_FG"
}

trace () {
    log "TRACE" "$1" "$ANSI_COLOR_GRAY_FG"
}