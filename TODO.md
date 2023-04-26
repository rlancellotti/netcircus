# Open tasks for NetCircus

## General code organization

- Create 2 packages (backend, gui)
- Support start/stop of backend from the gui
- Normalize terms and class names (element/component must be called in the same way - We choose component)
- Normalize paths for better integration with gnome (use .local/ directory)
- REfactor code if modules become too big.
- Add installation support (to do in a later phase)

## Backend improvements

- Auto detection of kernels and root filesystems
- Check code structure in hosts and switches. Do we need the backend_data structure? If so, can we avoid duplication?
- Add support for hostfs in hosts. Can be used for init scripts and for kernel modules
- Add support for modules in system UML using hostfs. Must distinguish between monolithic kernels and modular ones
- Improve support for component deletion/update
- Add support for additional consoles in hosts (accessible only from backend) for testing purposes.

## New features involving API

- Double check that update in hosts are propagated correctly in backend components
- Revise support for save/load to use API
- Add support for component status check via API. 
- Add support for deleting components/links
- Init scripts for hosts
- Init scripts for switches
- Support for save with filename
- Support for validation scripts (Very advanced task)

## GUI improvements

- Add edit dialog for switches (must also fix bug in API)
- Add context menu for cables
- Add edit dialog for cables (must also make this robust: avoid multiple cables on same interface)
- Add visual hint for host/switch names 
- Add visual hint for cable endpoints
- Add menu for save/load projects
- Add dialog for save/load projects
- Add visual feedback for component status in GUI (Running/Stopped)

## Hardening

- Check for code injection attacks
- Verify return codes in API
- Check data consistency in API
- Check forbidden actions. Some examples below.
- Save/load not allowed if network is running
- Editing of network not allowed if network is running
- Start not allowed if network is running
- Stop not allowed if network is stopped
- Change root filesystem must generate warning if cow file exists (possibly make entry not editable entry in dialog -- may require API change)