<?php

namespace App\Services;

use CodeIgniter\HTTP\Files\UploadedFile;
use RuntimeException;
use ZipArchive;

final class SpreadsheetReader
{
    public function read(UploadedFile $file): array
    {
        $extension = strtolower($file->getClientExtension());
        if (!in_array($extension, ['csv','xlsx'], true)) throw new RuntimeException('Upload a CSV or Excel .xlsx file.');
        if ($file->getSize() > 5 * 1024 * 1024) throw new RuntimeException('The participant list must be 5 MB or smaller.');
        $rows = $extension === 'csv' ? $this->csv($file->getTempName()) : $this->xlsx($file->getTempName());
        if (!$rows) throw new RuntimeException('The uploaded file is empty.');
        $headers = array_map([$this, 'header'], array_shift($rows));
        $records = [];
        foreach ($rows as $row) {
            if (!array_filter($row, fn($value)=>trim((string)$value)!=='')) continue;
            $record=[]; foreach($headers as $index=>$header) if($header!=='') $record[$header]=trim((string)($row[$index]??''));
            $records[]=$record;
            if(count($records)>500) throw new RuntimeException('A maximum of 500 participant rows can be imported at once.');
        }
        if (!$records) throw new RuntimeException('No participant rows were found below the header row.');
        return $records;
    }

    private function csv(string $path): array
    {
        $handle=fopen($path,'rb'); if(!$handle) throw new RuntimeException('Could not read the CSV file.');
        $rows=[]; while(($row=fgetcsv($handle))!==false)$rows[]=$row; fclose($handle); return $rows;
    }

    private function xlsx(string $path): array
    {
        $zip=new ZipArchive(); if($zip->open($path)!==true) throw new RuntimeException('The Excel file is invalid or damaged.');
        $shared=[]; $sharedXml=$zip->getFromName('xl/sharedStrings.xml');
        if($sharedXml!==false){$xml=simplexml_load_string($sharedXml);if($xml)foreach($xml->si as $item){$text=(string)$item->t;foreach($item->r as $run)$text.=(string)$run->t;$shared[]=$text;}}
        $sheetXml=$zip->getFromName('xl/worksheets/sheet1.xml'); $zip->close();
        if($sheetXml===false)throw new RuntimeException('The first Excel worksheet could not be read.');
        $xml=simplexml_load_string($sheetXml); if(!$xml)throw new RuntimeException('The Excel worksheet is invalid.');
        $rows=[]; foreach($xml->sheetData->row as $rowNode){$values=[];foreach($rowNode->c as $cell){$reference=(string)$cell['r'];preg_match('/[A-Z]+/',$reference,$matches);$index=$this->columnIndex($matches[0]??'A');$type=(string)$cell['t'];$value=$type==='inlineStr'?(string)$cell->is->t:(string)$cell->v;if($type==='s'&&isset($shared[(int)$value]))$value=$shared[(int)$value];$values[$index]=$value;}if($values){$width=max(array_keys($values))+1;$rows[]=array_map(fn($i)=>$values[$i]??'',range(0,$width-1));}}
        return $rows;
    }

    private function columnIndex(string $letters): int { $number=0;foreach(str_split($letters) as $letter)$number=$number*26+ord($letter)-64;return $number-1; }
    private function header(string $value): string { return trim(preg_replace('/_+/', '_', preg_replace('/[^a-z0-9]+/', '_', strtolower(trim($value)))),'_'); }
}