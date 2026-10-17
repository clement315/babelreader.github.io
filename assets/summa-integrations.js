/* Optional adapters for the standalone Summa reader.
 * Dictionary: set window.SUMMA_LOOKUP = ({word,language,location,selection}) => ...
 * or listen for document's "summa:word" event. Text rendering fires
 * "summa:render" with detail.container, including lang="la" elements.
 * Theme: call SummaReader.setTheme('dark'|'light'), or dispatch "babel:theme".
 * Do not import assets/reader.js: that file initializes the EPUB reader.
 */
(() => {
  document.addEventListener('dblclick',event=>{
    const column=event.target.closest('.cell[lang="la"]');
    if(!column)return;
    const selection=window.getSelection();const word=selection?.toString().trim()||'';
    if(!word||word.length>80||!/^[\p{L}\p{M}’'\-]+$/u.test(word))return;
    const detail={word,language:'la',location:window.SummaReader?.location,selection};
    document.dispatchEvent(new CustomEvent('summa:word',{detail}));
    if(typeof window.SUMMA_LOOKUP==='function')window.SUMMA_LOOKUP(detail);
  });
})();
