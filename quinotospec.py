#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess

# ANSI Color Codes for Premium Look
ORANGE = "\033[38;5;208m"
WHITE = "\033[1;37m"
BOLD = "\033[1m"
RESET = "\033[0m"
GREEN = "\033[92m"
RED = "\033[91m"

# Q logo matching the Quinoto brand: thick outer ring, inner gap, solid center, tail at bottom-right
QU_LOGO = f"""{ORANGE}                                    
                             
                *************                         
             *******************                      
           ***********************                    
         *********=-------=*********                  
        #*******=-----------=+********                
        ******=----+****+=----=*********              
       ******+---=********+-----=********             
       ******=--=***********+=----=*******            
       ******---=+************=-----+******           
       ******=---=**************=----+******          
        ******=----=*************+----******          
        *******+-----=************=---*******         
         ********+-----+**********----******          
           ********=----=+******+=--=+******          
            *********=-----====------=*****           
              *********=---------------=**            
                **********++++++**+=---=***            
                  ******************+=*******          
                    ***************** ******           
                        *********      ****
                                        **            
{RESET}
"""

def print_banner():
    print(QU_LOGO)
    print(f"{BOLD}QuinotoSpec CLI - Berserker Edition{RESET}")
    print(f"Enhancing AI Collaboration since 2024\n")

def run_install(args):
    """Calls the local install.sh script with appropriate flags."""
    print_banner()
    
    # Find the install.sh script. It should be in the same directory as this script 
    # if installed via symlink or in the package.
    script_dir = os.path.dirname(os.path.realpath(__file__))
    install_script = os.path.join(script_dir, "install.sh")
    
    if not os.path.exists(install_script):
        print(f"{RED}Error:{RESET} install.sh not found at {install_script}")
        sys.exit(1)
    
    command = ["bash", install_script]
    if args.opencode:
        command.append("--opencode")
    if args.cursor:
        command.append("--cursor")
    
    print(f"{GREEN}Starting installation...{RESET}")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError:
        print(f"\n{RED}Installation failed.{RESET}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="QuinotoSpec CLI")
    parser.add_argument("--opencode", action="store_true", help="Install for OpenCode (.opencode directory)")
    parser.add_argument("--cursor", action="store_true", help="Install for Cursor (.cursor directory)")
    parser.add_argument("--version", action="store_true", help="Show version information")
    
    # Default behavior is to run installation
    args = parser.parse_args()
    
    if args.version:
        print("QuinotoSpec CLI v1.0.0 (Berserker)")
        sys.exit(0)
    
    run_install(args)

if __name__ == "__main__":
    main()
