#!/usr/bin/env bash
# skill.sh — Install, update, and list skills from github.com/fea-lib/skills
#
# Usage:
#   install <skill-name> [--path /target/dir]
#   update  <skill-name>
#   list
#
# Pipe through curl:
#   curl -fsSL https://raw.githubusercontent.com/fea-lib/skills/main/scripts/skill.sh | bash -s install <skill-name>

set -euo pipefail

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REPO_URL="https://github.com/fea-lib/skills.git"
SKILLS_SUBDIR=".agents/skills"
DEFAULT_INSTALL_DIR="${HOME}/.agents/skills"

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------
die() { echo "Error: $*" >&2; exit 1; }
info() { echo "$*"; }
warn() { echo "Warning: $*" >&2; }

require_git() {
  command -v git >/dev/null 2>&1 || die "'git' is required but not installed."
}

# Create a temp dir and register cleanup on exit.
make_tmpdir() {
  local tmp
  tmp="$(mktemp -d)"
  trap "rm -rf '${tmp}'" EXIT
  echo "${tmp}"
}

# Sparse-clone the repo into $1, checking out path $2.
# If $2 is empty, only the root tree is fetched (for 'list').
sparse_clone() {
  local tmpdir="$1"
  local sparse_path="${2:-}"

  git clone \
    --quiet \
    --depth 1 \
    --filter=blob:none \
    --sparse \
    "${REPO_URL}" \
    "${tmpdir}" 2>&1 || die "Failed to fetch from ${REPO_URL}. Check your network connection."

  if [[ -n "${sparse_path}" ]]; then
    git -C "${tmpdir}" sparse-checkout set "${sparse_path}"
  fi
}

# Print skill name + first line of description from its SKILL.md.
print_skill_summary() {
  local skill_dir="$1"
  local skill_name
  skill_name="$(basename "${skill_dir}")"

  local desc=""
  if [[ -f "${skill_dir}/SKILL.md" ]]; then
    # Extract the description value from YAML frontmatter.
    # Handles single-line and folded (>) multi-line descriptions.
    desc="$(awk '
      /^---$/ { if (in_front++) exit; next }
      in_front && /^description:/ {
        sub(/^description:[[:space:]]*(>[[:space:]]*)?/, "")
        if ($0 != "") { print; exit }
        capture=1; next
      }
      capture && /^[[:space:]]/ { sub(/^[[:space:]]+/, ""); print; exit }
      capture { exit }
    ' "${skill_dir}/SKILL.md")"
  fi

  printf "  %-30s %s\n" "${skill_name}" "${desc}"
}

# ---------------------------------------------------------------------------
# confirm_path <resolved-path> <verb>
# Prints the resolved path and asks the user to confirm, correct, or abort.
# On success, sets CONFIRMED_PATH to the accepted path.
# ---------------------------------------------------------------------------
confirm_path() {
  local resolved="$1"
  local verb="$2"  # "Install to" or "Update in"

  while true; do
    printf "%s: %s\n" "${verb}" "${resolved}"
    printf "Confirm? [Y/n/new path]: "
    local answer
    read -r answer </dev/tty

    case "${answer}" in
      ""|Y|y)
        CONFIRMED_PATH="${resolved}"
        return 0
        ;;
      n|N)
        info "Aborted."
        exit 0
        ;;
      *)
        # Treat any other input as a new path.
        resolved="${answer/#\~/${HOME}}"  # expand leading ~
        ;;
    esac
  done
}

# ---------------------------------------------------------------------------
# cmd_list
# ---------------------------------------------------------------------------
cmd_list() {
  require_git

  info "Fetching available skills from ${REPO_URL} ..."
  local tmp
  tmp="$(make_tmpdir)"

  sparse_clone "${tmp}" "${SKILLS_SUBDIR}"

  local skills_root="${tmp}/${SKILLS_SUBDIR}"

  if [[ ! -d "${skills_root}" ]]; then
    info "No skills found in the repository."
    exit 0
  fi

  info ""
  info "Available skills (${REPO_URL%%.git}):"
  info ""

  local found=0
  for skill_dir in "${skills_root}"/*/; do
    [[ -d "${skill_dir}" ]] || continue
    print_skill_summary "${skill_dir}"
    found=1
  done

  if [[ "${found}" -eq 0 ]]; then
    info "  (no skills found)"
  fi

  info ""
}

# ---------------------------------------------------------------------------
# cmd_install <skill-name> [--path /dir]
# ---------------------------------------------------------------------------
cmd_install() {
  [[ $# -ge 1 ]] || die "Usage: skill install <skill-name> [--path /target/dir]"

  local skill_name="$1"
  shift

  local target_dir="${DEFAULT_INSTALL_DIR}"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --path)
        [[ $# -ge 2 ]] || die "--path requires an argument."
        target_dir="$2"
        shift 2
        ;;
      *)
        die "Unknown option: $1"
        ;;
    esac
  done

  # Expand ~ manually (handles cases where the value came from a variable).
  target_dir="${target_dir/#\~/${HOME}}"
  # Resolve to absolute path (handles relative paths like . or ./)
  target_dir="$(cd "${target_dir}" 2>/dev/null && pwd || echo "${target_dir}")"

  require_git

  # Confirm the install path with the user.
  CONFIRMED_PATH=""
  confirm_path "${target_dir}/${SKILLS_SUBDIR}/${skill_name}" "Install to"
  local install_dest="${CONFIRMED_PATH}"

  # Guard against reinstalling.
  if [[ -d "${install_dest}" ]]; then
    die "Skill '${skill_name}' is already installed at ${install_dest}. Use 'update' to update it."
  fi

  info "Fetching '${skill_name}' from ${REPO_URL} ..."
  local tmp
  tmp="$(make_tmpdir)"

  local remote_skill_path="${SKILLS_SUBDIR}/${skill_name}"
  sparse_clone "${tmp}" "${remote_skill_path}"

  local remote_skill_dir="${tmp}/${remote_skill_path}"

  if [[ ! -d "${remote_skill_dir}" ]]; then
    die "Skill '${skill_name}' does not exist in the repository. Run 'list' to see available skills."
  fi

  mkdir -p "$(dirname "${install_dest}")"
  cp -r "${remote_skill_dir}" "${install_dest}"

  info ""
  info "Installed '${skill_name}' to ${install_dest}"
}

# ---------------------------------------------------------------------------
# cmd_update <skill-name>
# ---------------------------------------------------------------------------
cmd_update() {
  [[ $# -ge 1 ]] || die "Usage: skill update <skill-name>"

  local skill_name="$1"

  require_git

  # ---------------------------------------------------------------------------
  # Path discovery: cwd → home → prompt
  # ---------------------------------------------------------------------------
  local install_dest=""

  local candidate_cwd="./${SKILLS_SUBDIR}/${skill_name}"
  local candidate_home="${HOME}/${SKILLS_SUBDIR}/${skill_name}"

  if [[ -d "${candidate_cwd}" ]]; then
    install_dest="$(cd "${candidate_cwd}" && pwd)"
    info "Found '${skill_name}' at ${install_dest}"
  elif [[ -d "${candidate_home}" ]]; then
    install_dest="${candidate_home}"
    info "Found '${skill_name}' at ${install_dest}"
  else
    warn "Could not find '${skill_name}' in ./${SKILLS_SUBDIR}/ or ${HOME}/${SKILLS_SUBDIR}/."
    printf "Enter the path to the installed skill directory: "
    read -r install_dest </dev/tty
    install_dest="${install_dest/#\~/${HOME}}"
    [[ -d "${install_dest}" ]] || die "Directory not found: ${install_dest}"
  fi

  info "Fetching latest '${skill_name}' from ${REPO_URL} ..."
  local tmp
  tmp="$(make_tmpdir)"

  local remote_skill_path="${SKILLS_SUBDIR}/${skill_name}"
  sparse_clone "${tmp}" "${remote_skill_path}"

  local remote_skill_dir="${tmp}/${remote_skill_path}"

  if [[ ! -d "${remote_skill_dir}" ]]; then
    die "Skill '${skill_name}' does not exist in the repository. Run 'list' to see available skills."
  fi

  # ---------------------------------------------------------------------------
  # Overwrite protection: warn if any local file differs from the remote copy.
  # mtime is not reliable for shallow clones (all files get the clone timestamp),
  # so we compare SHA-256 checksums instead.
  # ---------------------------------------------------------------------------
  local changed_files=()

  # Portable checksum: sha256sum (Linux) or shasum -a 256 (macOS).
  _sha256() {
    if command -v sha256sum >/dev/null 2>&1; then
      sha256sum "$1" | awk '{print $1}'
    else
      shasum -a 256 "$1" | awk '{print $1}'
    fi
  }

  while IFS= read -r -d '' remote_file; do
    local rel_path="${remote_file#${remote_skill_dir}/}"
    local local_file="${install_dest}/${rel_path}"

    if [[ -f "${local_file}" ]]; then
      local local_hash remote_hash
      local_hash="$(_sha256 "${local_file}")"
      remote_hash="$(_sha256 "${remote_file}")"
      if [[ "${local_hash}" != "${remote_hash}" ]]; then
        changed_files+=("${rel_path}")
      fi
    fi
  done < <(find "${remote_skill_dir}" -type f -print0)

  if [[ ${#changed_files[@]} -gt 0 ]]; then
    warn "The following local files differ from the remote version (may contain local edits):"
    for f in "${changed_files[@]}"; do
      echo "  - ${f}" >&2
    done
    printf "Overwrite anyway? [y/N]: "
    local answer
    read -r answer </dev/tty
    case "${answer}" in
      y|Y) ;;
      *)
        info "Aborted. No files were changed."
        exit 0
        ;;
    esac
  fi

  # ---------------------------------------------------------------------------
  # Copy new files over the installation directory.
  # ---------------------------------------------------------------------------
  local updated_files=()

  while IFS= read -r -d '' remote_file; do
    local rel_path="${remote_file#${remote_skill_dir}/}"
    local local_file="${install_dest}/${rel_path}"
    mkdir -p "$(dirname "${local_file}")"
    cp "${remote_file}" "${local_file}"
    updated_files+=("${rel_path}")
  done < <(find "${remote_skill_dir}" -type f -print0)

  info ""
  info "Updated '${skill_name}' at ${install_dest}:"
  for f in "${updated_files[@]}"; do
    echo "  ${f}"
  done
  info ""
  info "Done."
}

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
main() {
  [[ $# -ge 1 ]] || {
    echo "Usage:"
    echo "  skill install <skill-name> [--path /target/dir]"
    echo "  skill update  <skill-name>"
    echo "  skill list"
    exit 1
  }

  local cmd="$1"
  shift

  case "${cmd}" in
    install) cmd_install "$@" ;;
    update)  cmd_update  "$@" ;;
    list)    cmd_list    "$@" ;;
    *)
      die "Unknown command '${cmd}'. Valid commands: install, update, list"
      ;;
  esac
}

main "$@"
