#!/usr/bin/php -q
<?php

$INDIR="/smartmet/data/incoming/gts/sounding";
$OUTDIR="/smartmet/data/gts/sounding/world/querydata";
$EDITORDIR="/smartmet/editor/in";
$TMPDIR="/smartmet/tmp/data/sounding";
$TIMESTAMP=trim(`date +%Y%m%d%H%M`);
$OUTFILE="${TIMESTAMP}_gts_world_sounding.sqd";

system("mkdir -p ${TMPDIR}");

// 'm' modifier treats haystack as multi-line
$patterns = array("/TTAA[^=]+=/mU", "/TTBB[^=]+=/mU");

$files = glob("$INDIR/*");

$messages = array();
$types = array();
$dates = array();
$locations = array();
$output = "";

// search files for pattern and store found file names to arrays
foreach ($files as $file) {

  $contents = file_get_contents($file);

  foreach ($patterns as $pattern) {
    $matchArray= null;
    preg_match_all($pattern, $contents, $matchArray);
    
    foreach ($matchArray as $matches) {
      foreach ($matches as $match) {
	list($type, $date, $location) = preg_split("/\s+/", $match);
	$date = substr($date,0,4);
	$types[] = trim($type);
	$dates[] = trim($date);
	$locations[] = trim($location);
	
	$messages[$location][$date][$type] = trim(preg_replace("/\s+/"," ",$match));
      }
    }
  }
}

ksort($messages);
sort($types);
sort($dates);
sort($locations);

$types = array_unique($types);
$dates = array_unique($dates);
$locations = array_unique($locations);

foreach ($locations as $location) {
  foreach ($dates as $date) {
    foreach ($types as $type) {
      if (isset($messages[$location][$date][$type])) {
	$output .= $messages[$location][$date][$type] . "\r\n";
      }
    }
  }
}


$fp = fopen("$TMPDIR/$OUTFILE.txt", "wt");
if ($fp) {
  fwrite($fp, $output, strlen($output));
}
fclose($fp);

if (filesize("$TMPDIR/$OUTFILE.txt") > 0 ) 
    system("temp2qd -t $TMPDIR/$OUTFILE.txt > $TMPDIR/$OUTFILE");

    if (filesize("$TMPDIR/$OUTFILE") > 0 ) {
	rename("$TMPDIR/$OUTFILE","$OUTDIR/$OUTFILE");
	exec("cp -f $OUTDIR/$OUTFILE $EDITORDIR/");
	exec("rm -f $TMPDIR/$OUTFILE.txt");
      }

?>
