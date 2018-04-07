# Appabot
A customizable Discord notification bot for Pokemon GO spawns.
## Usage
New users should private message Appa `!home <lat, long>`, where `<lat, long>` is the coordinates of some home location.  
Then, set a radius with `!radius <minutes>`, where `<minutes>` is the maximum drive time from the specified home location. By default, `radius` is set to 100.  
To filter Pokemon notifications by IV, use `!filter <pokemon>:<IV>`. You can also set a default minimum IV by typing `!filter default:<IV>`. By default, the default IV is 80.
## Example usage
`!home 37.816866, -122.478290`  
`!radius 35`  
`!filter default:100`  
`!filter larvitar:90`, `!filter dratini:90`, `!filter chansey:90`, etc.
