#!/usr/bin/env bash
# Bash completion script for autovirt

_autovirt_completion() {
    local cur prev
    # Use built-in variables from bash completion
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Define all possible services
    local services="analytics artefact employee equipment logistics sales"
    
    # Define actions for each service
    local analytics_actions="daily-changes"
    local artefact_actions="renew"
    local employee_actions="set-required-salary set-demanded-salary"
    local equipment_actions="repair repair-with-offer"
    local logistics_actions="free-shop-storage optimize-unit-supplies optimize-shops-supplies"
    local sales_actions="manage-retail-prices"
    
    local sales_methods="middle-value twice-of-local price-and-quality complex-factors local-price"

    # Determine the current word position to complete
    case $COMP_CWORD in
        1)
            # Complete first argument (services)
            COMPREPLY=($(compgen -W "${services}" -- "${cur}"))
            ;;
        2)
            # Complete second argument (actions) based on first argument (service)
            case ${COMP_WORDS[1]} in
                analytics)
                    COMPREPLY=($(compgen -W "${analytics_actions}" -- "${cur}"))
                    ;;
                artefact)
                    COMPREPLY=($(compgen -W "${artefact_actions}" -- "${cur}"))
                    ;;
                employee)
                    COMPREPLY=($(compgen -W "${employee_actions}" -- "${cur}"))
                    ;;
                equipment)
                    COMPREPLY=($(compgen -W "${equipment_actions}" -- "${cur}"))
                    ;;
                logistics)
                    COMPREPLY=($(compgen -W "${logistics_actions}" -- "${cur}"))
                    ;;
                sales)
                    COMPREPLY=($(compgen -W "${sales_actions}" -- "${cur}"))
                    ;;
                *)
                    # If first argument is not a service, complete services
                    COMPREPLY=($(compgen -W "${services}" -- "${cur}"))
                    ;;
            esac
            ;;
        3)
            # Handle third argument based on service and action
            case ${COMP_WORDS[1]} in
                sales)
                    if [[ ${COMP_WORDS[2]} == "manage-retail-prices" ]]; then
                        # Don't complete for shop_id (numeric value)
                        return 0
                    fi
                    ;;
                logistics)
                    if [[ ${COMP_WORDS[2]} == "free-shop-storage" ]]; then
                        # Don't complete for shop_id (numeric value)
                        return 0
                    elif [[ ${COMP_WORDS[2]} == "optimize-unit-supplies" ]]; then
                        # Don't complete for unit_id (numeric value)
                        return 0
                    fi
                    ;;
                equipment)
                    if [[ ${COMP_WORDS[2]} == "repair" || ${COMP_WORDS[2]} == "repair-with-offer" ]]; then
                        # Don't complete for equipment_id (numeric value)
                        return 0
                    fi
                    ;;
            esac
            ;;
        *)
            # Handle flags and options
            case ${prev} in
                --method|-m)
                    COMPREPLY=($(compgen -W "${sales_methods}" -- "${cur}"))
                    return 0
                    ;;
                --factor|-f)
                    # Don't complete anything for factor value
                    return 0
                    ;;
                --units-only|-u|--units-exclude|-e)
                    # Don't complete anything for unit IDs
                    return 0
                    ;;
            esac

            # If current word starts with -, complete flags
            if [[ ${cur} == -* ]]; then
                case ${COMP_WORDS[1]} in
                    analytics)
                        if [[ ${COMP_WORDS[2]} == "daily-changes" ]]; then
                            COMPREPLY=($(compgen -W "--limit -l --help --dry-run" -- "${cur}"))
                        fi
                        ;;
                    equipment)
                        if [[ ${COMP_WORDS[2]} == "repair" || ${COMP_WORDS[2]} == "repair-with-offer" ]]; then
                            COMPREPLY=($(compgen -W "--units-only -u --units-exclude -e --keep_quality -k --offer -o --help --dry-run" -- "${cur}"))
                        fi
                        ;;
                    logistics)
                        if [[ ${COMP_WORDS[2]} == "optimize-unit-supplies" || ${COMP_WORDS[2]} == "optimize-shops-supplies" ]]; then
                            COMPREPLY=($(compgen -W "--factor -f --help --dry-run" -- "${cur}"))
                        fi
                        ;;
                    sales)
                        if [[ ${COMP_WORDS[2]} == "manage-retail-prices" ]]; then
                            COMPREPLY=($(compgen -W "--method -m --help --dry-run" -- "${cur}"))
                        fi
                        ;;
                    *)
                        COMPREPLY=($(compgen -W "--help --version --dry-run" -- "${cur}"))
                        ;;
                esac
            fi
            ;;
    esac
}

complete -F _autovirt_completion autovirt