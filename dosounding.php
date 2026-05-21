#!/usr/bin/php -q
<?php

$INDIR     = "/smartmet/data/incoming/gts/sounding";
$OUTDIR    = "/smartmet/data/gts/sounding/world/querydata";
$EDITORDIR = "/smartmet/editor/in";
$TMPDIR    = "/smartmet/tmp/data/sounding";
$TIMESTAMP = date('YmdHi');
$OUTFILE   = "{$TIMESTAMP}_gts_world_sounding.sqd";

if (!is_dir($TMPDIR) && !mkdir($TMPDIR, 0755, true)) {
    fwrite(STDERR, "Failed to create $TMPDIR\n");
    exit(1);
}

// 'm' treats input as multi-line, 'U' makes the [^=]+ non-greedy
$patterns = ["/TTAA[^=]+=/mU", "/TTBB[^=]+=/mU"];

$messages  = [];
$types     = [];
$dates     = [];
$locations = [];
$output    = "";

foreach (glob("$INDIR/*") as $file) {
    $contents = file_get_contents($file);
    if ($contents === false) {
        fwrite(STDERR, "Failed to read $file\n");
        continue;
    }

    foreach ($patterns as $pattern) {
        if (preg_match_all($pattern, $contents, $matchArray) === false) {
            continue;
        }
        foreach ($matchArray[0] as $match) {
            $tokens = preg_split("/\s+/", $match);
            if (count($tokens) < 3) {
                continue;
            }
            [$type, $date, $location] = $tokens;
            $date = substr($date, 0, 4);
            $type     = trim($type);
            $date     = trim($date);
            $location = trim($location);
            $types[]     = $type;
            $dates[]     = $date;
            $locations[] = $location;
            $messages[$location][$date][$type] = trim(preg_replace("/\s+/", " ", $match));
        }
    }
}

ksort($messages);
$types     = array_unique($types);     sort($types);
$dates     = array_unique($dates);     sort($dates);
$locations = array_unique($locations); sort($locations);

foreach ($locations as $location) {
    foreach ($dates as $date) {
        foreach ($types as $type) {
            if (isset($messages[$location][$date][$type])) {
                $output .= $messages[$location][$date][$type] . "\r\n";
            }
        }
    }
}

$txtfile = "$TMPDIR/$OUTFILE.txt";
$sqdfile = "$TMPDIR/$OUTFILE";

$fp = fopen($txtfile, "wt");
if ($fp === false) {
    fwrite(STDERR, "Failed to open $txtfile for writing\n");
    exit(1);
}
fwrite($fp, $output);
fclose($fp);

if (filesize($txtfile) > 0) {
    $exitCode = 0;
    system("temp2qd -t " . escapeshellarg($txtfile) . " > " . escapeshellarg($sqdfile), $exitCode);
    if ($exitCode === 0 && file_exists($sqdfile) && filesize($sqdfile) > 0) {
        if (!rename($sqdfile, "$OUTDIR/$OUTFILE")) {
            fwrite(STDERR, "Failed to move $sqdfile to $OUTDIR\n");
        } elseif (!copy("$OUTDIR/$OUTFILE", "$EDITORDIR/$OUTFILE")) {
            fwrite(STDERR, "Failed to copy $OUTFILE to $EDITORDIR\n");
        }
    } else {
        fwrite(STDERR, "temp2qd failed (exit=$exitCode) or produced empty output\n");
    }
}

if (file_exists($txtfile)) {
    unlink($txtfile);
}
