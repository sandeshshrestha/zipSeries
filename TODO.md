## Version 1.3
- [x] Support post restore command
- [x] Support multiply objects
   - [x] Support multiply objects from CLI
   - [x] Support multiply objects from config file
- [x] Support multiply object types
   - [x] Support multiply object types from CLI
   - [x] Support multiply object types from config file
- [x] Display job log
   - [x] Display job log when error occurs on the AS/400
   - [x] Support CLI options `--source-job-log` and `--target-job-log` that will echo the job after communiction with the server
   - [x] Support CLI options `--source-job-log-file $file` and `--target-job-log-file $file` that will write the job after communiction with the server


## Version 1.4
- [ ] Support pre restore command
- [ ] Support multiply libraries
- [ ] Add option `--source-backup-save-file` and `--target-backup-save-file` that will take a backup of the current objects / libraries before restoring
   - the save file should support the wildcard `%d` or `%n` that will create files named: where `--*-backup-save-file backup-%n.4zs` will create `backup-1.4zs`, `backup-2.4zs`, ... and where `--*-backup-save-file backup-%d.4zs` will create `backup-$(date +%Y-%m-%d-%H-%M-%S)`, eg. `backup-2015-10-21-22-37-05.4zs`
- [x] Add option `--job-log` as an alias for `--source-job-log --target-job-log`
- [x] Add option `--job-log-file $file` as an alias for `--source-job-log-file $file --target-job-log-file $file`
