<?php
    $file_path = '/home/ubuntu/ferroviaDrone/output3d.zip';
    $filename = 'output3d.zip';
    if(!file_exists($file_path)){ // file does not exist
        die('file not found');
    } else {
        header("Content-type: application/zip"); 
        header("Content-Disposition: attachment; filename=$filename");
        header("Content-length: " . filesize($filename));
        header("Pragma: no-cache"); 
        header("Expires: 0"); 
        readfile("$file_path");
    }
?>